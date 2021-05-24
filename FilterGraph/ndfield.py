from typing import Tuple
from FilterGraph.axes import axis_info
import numpy as np

def identity_count(iterable, value):
    return [x is value for x in iterable].count(True)

class ndfield:
    """
    N-Dimensional field, mapping the coordinates in a space to either scalars, vectors or objects
    conceptual extension of np.ndarray, with arbitrary axes (not just ints from 0)

    subclasses should at least overload axes and __getitem__
    """
    
    @property
    def axes(self) -> Tuple(axis_info):
        raise NotImplementedError

    @property
    def dtype(self):
        "defaults to np.float_"
        return np.float_

    @property
    def shape(self):
        "default implementation calculates the shape from the axes"
        return tuple([a.size for a in self.axes])
    
    def expand_ellipsis(self, key):
        "convenience function to complete the key for all axes"
        n = len(self.axes)
        if not isinstance(key, tuple):
            key = (key,)
        if identity_count(key, np.newaxis) > 0:
            raise NotImplementedError("np.newaxis is not supported yet")
        if len(key) > n:
            raise IndexError
        el = identity_count(key, ...)
        if el > 1:
            raise IndexError
        if el == 1:
            el = key.index(...)
            return key[:el] + (np.s_[:], ) * (n - len(key)+1) + key[el+1:]
        else:
            return key + (np.s_[:], ) * (n - len(key))

    def __getitem__(self, indexes):
        raise NotImplementedError
    
    def __len__(self):
        return self.size
    
    @property
    def size(self):
        return np.prod(self.shape)

    def __array__(self, dtype = None):
        if all([a.countable for a in self.axes]):
            if dtype == None:
                dtype = self.dtype
            return np.array(self[...], dtype=dtype)
        else:
            # warnings.warn("not sure this is the right way to do it... maybe numpy will raise...")
            raise AttributeError