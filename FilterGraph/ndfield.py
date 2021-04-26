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

    @property
    def samplespace(self):
        raise NotImplementedError

    @property
    def dtype(self):
        raise NotImplementedError

    @property
    def shape(self):
        "default implementation calculates the number from the axes"
        return [a.lenght for a in self.axes]

    @autocreate
    class coordspace:
        parent = cdh.parent_reference()

        def __getitem__(self, x):
            return self.parent.samplespace[self.parent.to_index(x)]

    def to_index(self, x):
        if not isinstance(x, tuple):
            return self.axes[0].to_index(x)
        return tuple([a.to_index(xx) for a, xx in zip(self.axes, x)])
    
    def from_index(self, i):
        if not isinstance(i, tuple):
            return self.axes[0].from_index(i)
        return tuple([a.from_index(ii) for a, ii in zip(self.axes, i)])

    def __getitem__(self, i):
        return self.samplespace[i]

    def __array__(self, dtype = None):
        if all([(a.nsamples != None and a.nsamples < np.inf) for a in self.axes]):
            if dtype == None:
                dtype = self.dtype
            return np.array(self.samplespace[...], dtype=dtype)
        else:
            return None #not sure this is the right way to do it... maybe numpy will raise...