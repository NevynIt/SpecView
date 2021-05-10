import class_definition_helpers as cdh
import numbers
import numpy as np
import warnings
import itertools
from .axes import *

class base_field_sampler:
    def __init__(self, axes):
        self.axes = axes
        self.axes_interp = [a.get_sampler(i) for i, a in enumerate(axes)]

    def identify_indexes(self, indexes):
        "collect the required indexes from each axis in order (which also prepares the samplers)"
        self.desired_indexes = indexes
        required_indexes = []
        for ai,di in zip(self.axes_interp, indexes):
            if isinstance(di, numbers.Number):
                #wrap the scalar indexes, this is needed to make sure samplers work on the right axis
                di = np.array([di])
            required_indexes.append(ai.identify_indexes(di))
        return tuple(required_indexes)

    def sample(self, space, indexes):
        return space[indexes]

    def calculate_values(self, values):
        #ask each axis in order to perform the interpolation
        for i, ai in enumerate(self.axes_interp):
            values = ai.calculate_values(values)

        #squeeze the axes where the index was a scalar
        scalars = [isinstance(di, numbers.Number) for di in self.desired_indexes]
        if any(scalars):
            values = np.squeeze(values, np.arange(len(indexes))[scalars])
        
        return values
    
    def interpolate(self, space, indexes):
        if all([(type(i) == base_axis_sampler) for i in self.axes_interp]):
            return self.sample(space, indexes)

        #identify the required indexes
        indexes = self.identify_indexes(indexes)

        #sample the space
        values = self.sample(space, indexes)

        return self.calculate_values(values)

class combined_field_sampler(base_axis_sampler):
    def __init__(self, samplers, axes):
        self.chain = []
        self.axes = axes
        for s in samplers:
            inst = s(self.axes)
            self.chain.append(inst)
            self.axes = inst.axes
        self.chain = tuple(self.chain)
    
    def identify_indexes(self, di):
        for s in self.chain:
            di = s.identify_indexes(di)
        return di
    
    def calculate_values(self, rv):
        for s in reversed(self.chain):
            rv = s.calculate_values(rv)
        return rv

class ndfield:
    """
    N-Dimensional field, mapping the coordinates in a space to either scalars, vectors or objects
    conceptual extension of np.ndarray, with arbitrary axes (not just ints from 0)

    subclasses should at least overload axes and samplespace
    """
    
    @property
    def axes(self):
        raise NotImplementedError

    def samplespace(self, indexes):
        "samplespace is indexed with a iterable of slices/indexes/arrays of indexes, one per axis."
        raise NotImplementedError

    @property
    def dtype(self):
        return np.float_

    @property
    def shape(self):
        "default implementation calculates the shape from the axes"
        return tuple([a.index_domain.nsamples for a in self.axes])

    sampler = cdh.default( base_field_sampler )

    def get_sampler(self):
        return self.sampler(self.axes)

    @cdh.indexable
    def coordspace(self, coords):
        return self.indexspace[self.to_indexes(coords)]

    def expand_ellipsis(self, key):
        n = len(self.axes)
        if not isinstance(key, tuple):
            key = (key,)
        if key.count(np.newaxis) > 0:
            raise NotImplementedError("np.newaxis is not supported yet")
        if len(key) > n:
            raise IndexError
        el = key.count(...)
        if el > 1:
            raise IndexError
        if el == 1:
            el = key.index(...)
            return key[:el] + (EMPTY_SLICE, ) * (n - len(key)+1) + key[el+1:]
        else:
            return key + (EMPTY_SLICE, ) * (n - len(key))

    def to_indexes(self, coords):
        return tuple([a.to_index(c) for a, c in zip(self.axes, self.expand_ellipsis(coords))])
    
    def from_indexes(self, indexes):
        return tuple([a.from_index(i) for a, i in zip(self.axes, self.expand_ellipsis(indexes))])
    
    @cdh.indexable
    def indexspace(self, indexes):
        return self.get_sampler().interpolate(self.samplespace, self.expand_ellipsis(indexes))

    def __getitem__(self, indexes):
        return self.indexspace(indexes)

    def __array__(self, dtype = None):
        if all([a.countable for a in self.axes]):
            if dtype == None:
                dtype = self.dtype
            return np.array(self[...], dtype=dtype)
        else:
            warnings.warn("not sure this is the right way to do it... maybe numpy will raise...")
            return None