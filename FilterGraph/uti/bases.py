from autoinit import autoinit
import numpy as np
import enum, copy

class frequency_scales(enum.Enum):
    NONE = 0
    LINEAR = 1
    LOGARITMIC = 2

@autoinit(
    pre={
        "channels": 0,
        "framerate": 0,
        "freq_bins": 0,
        "freq_scale": frequency_scales.NONE,
        "nyquist": 0,
        "framerange": 
    }
)
class Descriptor:
    def copy(self):
        return copy.copy(self)

class Source:
    def read(nframes: int):
        raise NotImplementedError
    
    @property
    def descriptor(self):
        raise NotImplementedError
    
    def seek(self, pos: int):
        raise NotImplementedError
    
    def tell(self) -> int:
        

class Sink:
    pass

class Transform:
    pass
