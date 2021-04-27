import class_definition_helpers as cdh
from .axes import *

class ndfield:
    """
    N-Dimensional field, mapping the coordinates in a space to either scalars, vectors or objects
    conceptual extension of np.ndarray, with arbitrary axes (not just ints from 0)

    subclasses should at least overload axes, dtype and samplespace
    """
    
    @property
    def axes(self):
        raise NotImplementedError

    def samplespace(self, i):
        "samplespace gets asked for a grid of indexes. i.e.: i is an array of M arrays, with M = len(shape)"
        raise NotImplementedError

    @property
    def dtype(self):
        raise NotImplementedError

    @property
    def shape(self):
        "default implementation calculates the shape from the axes"
        return tuple([a.lenght for a in self.axes])

    @cdh.autocreate
    class interpolator(interpolator_base):
        """Uses the interpolators from each axis, in sequence, to interpolate over n-dimensions"""
        parent = cdh.parent_reference()

        def find_indexes(self, i):
            raise NotImplementedError
        
        def interpolate(self, i, ip, vp):
            raise NotImplementedError

    def coordspace(self, x):
        return self[self.to_index(x)]

    def to_index(self, x):
        if not isinstance(x, tuple):
            return self.axes[0].to_index(x)
        return tuple([a.to_index(xx) for a, xx in zip(self.axes, x)])
    
    def from_index(self, i):
        if not isinstance(i, tuple):
            return self.axes[0].from_index(i)
        return tuple([a.from_index(ii) for a, ii in zip(self.axes, i)])

    def __getitem__(self, key):
        #transform key in specific indexes
        if not isinstance(key, tuple):
            key = (key,)
        if len(key) > len(self.axes):
            raise IndexError
        el = sum([i == ... for i in key])
        if el > 1:
            raise IndexError
        elif el == 1:
            raise NotImplementedError
        else:
            key = key + (slice(), ) * (len(key) - len(self.axes))
        ind = []
        for i in range(len(key)):
            k = key[i]
            if isinstance(k, slice):
                if k == slice():
                    ind.append(self.axes[i].index_domain.arange())
                else:
                    sl = slice(k.start or self.axes[i].index_domain.start, k.stop or self.axes[i].index_domain.stop, k.step or self.axes[i].index_domain.step)
                    if sl.step == None or sl.step == 0 or l == np.inf:
                        raise IndexError
                    ind.append(np.arange(sl.start,sl.stop,sl.step))
            elif isinstance(k, numbers.Number):
                ind.append(np.asarray(k)) #TODO: not sure here
            else: #assume it's a ndarray, TODO more checking
                ind.append(k)
        ind = np.asarray(ind)
        ip = self.interpolator.find_indexes(ind)
        vp = self.samplespace(ip)
        return self.interpolator.interpolate(ind, ip, vp)

    def __array__(self, dtype = None):
        if all([(a.nsamples != None and a.nsamples < np.inf) for a in self.axes]):
            if dtype == None:
                dtype = self.dtype
            return np.array(self.samplespace(...), dtype=dtype)
        else:
            return None #not sure this is the right way to do it... maybe numpy will raise...