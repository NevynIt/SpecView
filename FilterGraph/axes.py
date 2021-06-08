from typing import Tuple
import class_definition_helpers as cdh
import numpy as np
from dataclasses import dataclass

@dataclass
class axis_info:
    size: int = np.inf
    lbound: int = None
    ubound: int = None
    unit: str = ""
    annotations: Tuple[str] = ()

    def __post_init__(self):
        if self.size <= 0:
            raise ValueError("axis size must be > 0")
        if self.countable:
            if self.lbound is None:
                self.lbound	= 0
            if self.ubound is None:
                self.ubound = self.lbound + self.size - 1
            if self.size == 1 and self.lbound != self.ubound:
                raise ValueError("size == 1 must imply lbound == ubound")
        else:
            if self.lbound is None:
                self.lbound = 0
            if self.ubound is None:
                self.ubound = np.inf

    @property
    def countable(self) -> bool:
        return self.size < np.inf

    def update_slice(self, sl = slice(None)) -> slice:
        if self.size == 1:
            step = 1
        else:
            step = (self.ubound - self.lbound)/(self.size-1)
            if step % 1 == 0:
                step = int(step)
        step = sl.step or step
        if step > 0:
            if sl.start is None:
                start = self.lbound
            else:
                start = sl.start
            if sl.stop is None:
                stop = self.ubound + step
            else:
                stop = sl.stop
        elif step < 0:
            # warnings.warn("maybe incorrect, boundaries might be wrong")
            if sl.start is None:
                start = self.ubound
            else:
                start = sl.start
            if sl.stop is None:
                stop = self.lbound - step
            else:
                stop = sl.stop
        return slice(start,stop,step)
    
    def arange(self):
        return np.linspace(self.lbound, self.ubound, self.size)

    def to_index(self, x):
        raise NotImplementedError

    def to_coord(self, x):
        raise NotImplementedError

@dataclass
class linear_axis_info(axis_info):
    origin: float = 0 #coordinate of index 0
    step: float = 1 #delta coordinate for each unit of index

    @property
    def sampling_rate(self):
        return 1/self.step

    def __to_index(self, x):
        return (x - self.origin)/self.step

    def to_index(self, x):
        if isinstance(x, slice):
            sl = self.update_slice()
            sl = slice(self.__to_coord(sl.start), self.__to_coord(sl.stop), self.step)
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
            sl = self.update_slice()
            return slice(
                self.__to_coord(sl.start if x.start is None else x.start),
                self.__to_coord(sl.stop if x.stop is None else x.stop),
                (x.step or sl.step)*self.step
            )
        else:
            return self.__to_coord(x)

@dataclass
class log_axis_info(axis_info):
    scale: float = 1 #coordinate of index 0
    base: float = 2 #delta coordinate for each unit of index

    def __to_index(self, x):
        return (x - self.origin)/self.step

    def to_index(self, x):
        if isinstance(x, slice):
            if x.step is None:
                size = self.size
            elif x.start is None or x.stop is None:
                raise NotImplementedError("Inference of number of sample not implemented for automatically inferred bounds")
            else:
                size = (x.stop - x.start) / x.step
            lbound = self.lbound if x.start is None else x.start
            ubound = self.ubound if x.stop is None else x.stop
            x = np.linspace(lbound, ubound, size)
        return self.__to_index(x)

    def __to_coord(self, x):
        return np.power(self.base,x) * self.scale

    def to_coord(self, x):
        if isinstance(x, slice):
            x = self.update_slice(x)
            x = np.arange(x.start, x.stop, x.step)
        return self.__to_coord(x)