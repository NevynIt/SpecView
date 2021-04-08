from autoinit import autoinit
import numpy as np
import enum, copy

@autoinit(
    pre={
        "name": None,
        "entries": 0,
        "start": 0,
        "end": 0,
        "scale": None
    }
)
class Axis:
    pass

class Source:
    def read(entries, advance = True):
        raise NotImplementedError
    
    @property
    def descriptor(self):
        raise NotImplementedError
    
    def seek(self, pos, absolute = True):
        raise NotImplementedError
    
    def tell(self):
        raise NotImplementedError
    
    @property
    def position(self):
        return self.tell()

    @position.setter
    def position(self, value):
        self.seek(value)

class Sink:
    def write(signal, advance = True):
        raise NotImplementedError
    
    @property
    def descriptor(self):
        raise NotImplementedError
    
    def seek(self, pos, absolute = True):
        raise NotImplementedError
    
    def tell(self):
        raise NotImplementedError
    
    @property
    def position(self):
        return self.tell()

    @position.setter
    def position(self, value):
        self.seek(value)

class Transform:
    @property
    def direction(self):
        raise NotImplementedError
    
    @direction.setter
    def direction(self, value):
        raise NotImplementedError
    
    @property
    def descriptor(self):
        raise NotImplementedError

    def pump(self, entries):
        raise NotImplementedError
    
    def seek(self, pos, absolute = True):
        raise NotImplementedError
    
    def tell(self):
        raise NotImplementedError
    
    @property
    def position(self):
        return self.tell()

    @position.setter
    def position(self, value):
        self.seek(value)

if __name__ == "__main__":
    a = Axis()
    print(1)