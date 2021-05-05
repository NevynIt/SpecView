import class_definition_helpers as cdh
import numbers
import numpy as np
import warnings
import itertools
from .axes import *

        
class field_interpolator:
    props = cdh.property_store()
    
    def __init__(self, axes):
        self.axes_interp = [a.interpolator for a in axes]
        
    axes_interp = props.reactive()
    desired_indexes = props.reactive()

    @props.cached(desired_indexes, axes_interp)
    def required_indexes(self):
        "collect the required indexes from each axis in order (which also prepares the interpolators)"
        raise NotImplementedError
        
    required_values = props.reactive()
   
    @props.cached(required_values, axes_interp, required_indexes)
    def desired_values(self):
        "ask each axis in order to perform the interpolation"
        raise NotImplementedError

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

    @property
    def interpolator(self):
        "get a thread specific interpolator object"
        return axis_interpolator(self.axes)

    @cdh.indexable
    def coordspace(self, coords):
        return self.indexspace[self.to_indexes(coords)]

    def to_indexes(self, coords):
        return tuple([a.to_index(c) for a, c in zip(self.axes, self.expand_ellipsis(coords))])
    
    def from_indexes(self, indexes):
        return tuple([a.from_index(i) for a, i in zip(self.axes, self.expand_ellipsis(indexes))])
    
    #TODO: use the new interpolator class
    @cdh.indexable
    def indexspace(self, indexes):
        interp = self.interpolator
        interp.desired_indexes = indexes
        interp.required_values = self.samplespace(interp.required_indexes)
        return interp.desired_values

    # @cdh.indexable
    # def indexspace(self, indexes):
    #     ind = self.expand_ellipsis(indexes)
    #     ind, samples = self.to_samples(ind)
    #     #TODO: process the sub-sample-spaces from blocks one by one
    #     #use itertools.product
    #     values = self.samplespace(samples)
    #     #combine the blocks in a values matrix
    #     return self.interpolate(ind, samples, values)

    def to_samples(self, indexes):
        samples = []
        ind = []
        for a, i in zip(self.axes, self.expand_ellipsis(indexes)):
            i1, s = a.to_samples(i)
            samples.append(s)
            ind.append(i1)
        return (tuple(ind), tuple(s))
  
    def interpolate(self, indexes, samples, values):
        "interpolate starting from the last dimension"
        for i in range(len(indexes))[::-1]:
            vp = self.parent.axes[i].interpolate(indexes[i], samples[i], values, i)
        return vp

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

# class fnc_field(ndfield):
#     def fnc(self, grid):
#         return grid.sum(0)
    
#     @cdh.indexable
#     def samplespace(self, indexes):
#         return self.fnc(np.mgrid[indexes])