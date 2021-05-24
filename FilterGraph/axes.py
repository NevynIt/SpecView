import class_definition_helpers as cdh
import numpy as np
from dataclasses import dataclass

@dataclass
class axis_info:
    origin: float = 0 #coordinate of index 0
    step: float = 1 #delta coordinate for each unit of index
    steps_forwards: float = np.inf #number of samples in the direction of step (including the one at the origin)
    steps_backwards: float = np.inf #number of samples in the direction opposite of step
    unit: str = ""
    annotations: tuple = ()

    @property
    def sampling_rate(self):
        return 1/self.step

    @property
    def size(self):
        return max(0, self.steps_forwards + self.steps_backwards)
    
    @property
    def countable(self) -> bool:
        return self.size < np.inf

    @property
    def lenght(self):
        return self.size * self.step

    @property
    def index_slice(self):
        return slice(-self.steps_backwards,self.steps_forwards,1)
    
    def update_slice(self, sl):
        domain = self.index_slice
        step = sl.step or 1
        if step > 0:
            if sl.start is None:
                start = domain.start
            else:
                start = sl.start
            if sl.stop is None:
                stop = domain.stop
            else:
                stop = sl.stop
        elif step < 0:
            # warnings.warn("maybe incorrect, boundaries might be wrong")
            if sl.start is None:
                start = domain.stop - domain.step
            else:
                start = sl.start
            if sl.stop is None:
                stop = domain.start - domain.step
            else:
                stop = sl.stop
        return slice(start,stop,step)

    @property
    def coord_slice(self):
        return slice(self.origin-self.steps_backwards*self.step,self.origin+self.steps_forwards*self.step,self.step)

    def __to_index(self, x):
        return (x - self.origin)/self.step

    def to_index(self, x):
        if isinstance(x, slice):
            sl = self.coord_slice
            return slice(
                self.__to_index(sl.start if x.start is None else x.start),
                self.__to_index(sl.stop if x.stop is None else x.stop),
                (x.step or sl.step)/self.step
            )
        else:
            return self.__to_index(x)

    def __to_coord(self, x):
        return self.origin + x*self.step

    def to_coord(self, x):
        if isinstance(x, slice):
            sl = self.index_slice
            return slice(
                self.__to_coord(sl.start if x.start is None else x.start),
                self.__to_coord(sl.stop if x.stop is None else x.stop),
                (x.step or sl.step)*self.step
            )
        else:
            return self.__to_coord(x)