import class_definition_helpers as cdh
import numbers
import numpy as np
import warnings
import itertools
from .axes import *

class base_field_interpolator:
    props = cdh.property_store()
    def __init__(self, field):
        pass

    def interpolate(self, space, indexes):
        return space[indexes]

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

    interpolator = cdh.default( base_field_interpolator )

    def get_interpolator(self):
        return self.interpolator(self.axes)

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
        return self.get_interpolator().interpolate(self.samplespace, self.expand_ellipsis(indexes))

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