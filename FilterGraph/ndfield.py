import class_definition_helpers as cdh
from .axes import *

def expand_slices(key: tuple[any], domains: list[domain]):
    #transform key in specific indexes
    if not isinstance(key, tuple):
        key = (key,)
    if len(key) > len(domains):
        raise IndexError
    el = key.count(...)
    if el > 1:
        raise IndexError
    if el == 1:
        el = key.index(...)
        key = key[:el] + (EMPTY_SLICE, ) * (len(domains) - len(key)+1) + key[el+1:]
    else:
        key = key + (EMPTY_SLICE, ) * (len(domains) - len(key))
    ind = []
    for i in range(len(key)):
        k = key[i]
        if isinstance(k, slice):
            domain_slice = domains[i].slice()
            if k == EMPTY_SLICE or k == domain_slice:
                ind.append(domain_slice)
            else:
                step = k.step or domain_slice.step
                if step == 0:
                    raise IndexError
                elif step>0:
                    start = k.start or domain_slice.start
                    start = max(start, domain_slice.start)
                    stop = k.stop or domain_slice.stop
                    stop = min(stop, domain_slice.stop)
                else:
                    start = k.start or domain_slice.start
                    start = max(start, domain_slice.start)
                    stop = k.stop or domain_slice.stop
                    stop = min(stop, domain_slice.stop)
                n = max(0,(stop-start)/step)
                if n == np.inf:
                    raise IndexError
                ind.append(slice(start,stop,step))
        else: #anything else, keep it as it is
            ind.append(k)
    return tuple(ind)

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
        "samplespace is indexed with a iterable of slices/indexes/arrays of indexes, one per axis."
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

        def find_indexes(self, coords):
            #find all indexes in parallel
            ip = []
            for i, a in zip(coords,parent.axes):
                if a.interpolator:
                    ip.append(a.interpolator.find_indexes(i))
                else:
                    ip.append(i)
            return ip
        
        def interpolate(self, coords, ip, vp):
            #interpolate starting from the last dimension
            #TODO: TEST TEST TEEEEST
            for i in range(len(i))[::-1]:
                a = parent.axes[i]
                if a.interpolator:
                    vp = a.interpolator.interpolate(coords[i], ip[i], vp, i)
                else:
                    pass
            return vp

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
        ind = expand_slices(key, [a.index_domain for a in self.axes])
        if self.interpolator:
            ip = self.interpolator.find_indexes(ind)
            vp = self.samplespace(ip)
            return self.interpolator.interpolate(ind, ip, vp)
        else:
            return self.samplespace(ind)

    def __array__(self, dtype = None):
        if all([a.countable for a in self.axes]):
            if dtype == None:
                dtype = self.dtype
            return np.array(self[...], dtype=dtype)
        else:
            return None #not sure this is the right way to do it... maybe numpy will raise...