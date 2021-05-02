import class_definition_helpers as cdh
import numbers
import numpy as np
import warnings
from .axes import *

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

    @cdh.autocreate
    class interpolator(interpolator_base):
        """Uses the interpolators from each axis, in sequence, to interpolate over n-dimensions"""
        parent = cdh.parent_reference()

        def find_indexes(self, indexes):
            "find all indexes in parallel"
            ip = []
            for i, a in zip(indexes,self.parent.axes):
                if a.interpolator:
                    ip.append(a.interpolator.find_indexes(i))
                else:
                    ip.append(i)
            return tuple(ip)
        
        def interpolate(self, indexes, ip, vp):
            "interpolate starting from the last dimension"
            for i in range(len(indexes))[::-1]:
                vp = self.parent.axes[i].interpolator.interpolate(indexes[i], ip[i], vp, i)
            return vp

    @cdh.indexable
    def coordspace(self, coords):
        return self[self.to_index(coords)]

    @cdh.indexable
    def outerspace(self, indexes):
        raise NotImplementedError

    @cdh.indexable
    def indexspace(self, indexes):
        domains = [a.index_domain for a in self.axes]
        #split ip in areas within the sample space and areas outside, axis per axis
        #-> ind is a tuple with len equal to len(axes)
        #   create 3 indexes per element of ind (things < start, things in between, things > stop)
        #      single scalar indexes are easy, the scalar goes in one of the bins and the others are empty
        #      slices are slightly more complicated, one slice could become up to three slices
        #      ndarrays should be first sorted, then split with the same logic as the simple scalar

        # 3d example: [[None,sliceA,None],[sliceB1,sliceB2,None],[ndarrayC1, ndarrayC2, ndarrayC3]]
        # this becomes conceptally a 3d array with shape (3,3,3), but some dimensions can be reduced and
        # this becomes a 3d array with shape (1,2,3) and contents:
        # [ [ (sliceA,sliceB1,ndarrayC1),(sliceA,sliceB1,ndarrayC2),(sliceA,sliceB1,ndarrayC3) ],
        #   [ (sliceA,sliceB2,ndarrayC1),(sliceA,sliceB2,ndarrayC2),(sliceA,sliceB2,ndarrayC3) ] ]

        #iterate all the combinations equivalent to the subspaces that are inside/outside one or more axes
        #call samplespace for the single one inside, if any. (sliceA,sliceB2,ndarrayC2) in the example above
        #call outerspace for the ones outside (all the others)
        vp = self.samplespace(indexes)
        #recombine the pieces into a single ndarray (using numpy.blocks), based on how things had been cut
        #      single scalar indexes are easy, the bit with the scalar is the only thing used
        #      slices are slightly more complicated, as up to three pieces could be collated
        #      ndarrays should be first collated and then reshuffled
        #reshuffle the ndarray axes to come back to the order requested initially
        return vp

    def to_index(self, coords):
        if not isinstance(coords, tuple):
            return self.axes[0].to_index(coords)
        return tuple([a.to_index(c) for a, c in zip(self.axes, coords)])
    
    def from_index(self, indexes):
        if not isinstance(i, tuple):
            return self.axes[0].from_index(indexes)
        return tuple([a.from_index(i) for a, i in zip(self.axes, indexes)])

    def __getitem__(self, indexes):
        ind = self.expand_indexes(indexes)
        ip = self.interpolator.find_indexes(ind)
        vp = self.indexspace(ip)
        return self.interpolator.interpolate(ind, ip, vp)

    def __array__(self, dtype = None):
        if all([a.countable for a in self.axes]):
            if dtype == None:
                dtype = self.dtype
            return np.array(self[...], dtype=dtype)
        else:
            warnings.warn("not sure this is the right way to do it... maybe numpy will raise...")
            return None

    def expand_indexes(self, indexes, constrain_bounds = True):
        domains = [a.index_domain for a in self.axes]
        #transform key in specific indexes
        if not isinstance(indexes, tuple):
            indexes = (indexes,)
        if len(indexes) > len(domains):
            raise IndexError
        el = indexes.count(...)
        if el > 1:
            raise IndexError
        if el == 1:
            el = indexes.index(...)
            indexes = indexes[:el] + (EMPTY_SLICE, ) * (len(domains) - len(indexes)+1) + key[el+1:]
        else:
            indexes = indexes + (EMPTY_SLICE, ) * (len(domains) - len(indexes))
        ind = []
        for i in range(len(indexes)):
            k = indexes[i]
            if isinstance(k, slice):
                domain_slice = domains[i].slice()
                if k == EMPTY_SLICE or k == domain_slice:
                    ind.append(domain_slice)
                else:
                    step = k.step or domain_slice.step
                    if step == 0 or step == None:
                        raise IndexError
                    if step <0:
                        warnings.warn("maybe incorrect, boundaries might be wrong")
                        start = k.start or (domain_slice.stop - domain_slice.step)
                        stop = k.stop or (domain_slice.start - domain_slice.step)
                        if constrain_bounds:
                            start = min(start, domain_slice.stop - domain_slice.step)
                            stop = max(stop, domain_slice.start - domain_slice.step)
                    else:
                        start = k.start or domain_slice.start
                        stop = k.stop or domain_slice.stop
                        if constrain_bounds:
                            start = max(start, domain_slice.start)
                            stop = min(stop, domain_slice.stop)
                    n = max(0,(stop-start)/step)
                    if n == np.inf:
                        raise IndexError
                    ind.append(slice(start,stop,step))
            elif isinstance(k, numbers.Number):
                    ind.append(k)
            else:
                k = np.asanyarray(k)
                if issubclass(k.dtype.type, numbers.Integral):
                    ind.append(k)
                elif k.dtype == np.bool_:
                    raise NotImplementedError
                else:
                    raise IndexError
        return tuple(ind)

# class fnc_field(ndfield):
#     def fnc(self, grid):
#         return grid.sum(0)
    
#     @cdh.indexable
#     def samplespace(self, indexes):
#         return self.fnc(np.mgrid[indexes])