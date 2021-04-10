from decorators import *
import numpy as np
import enum, copy

class Axis:
    @assignargs(
        name= None,
        entries= 0,
        start= 0,
        end= 0,
        scale= None
        )
    def __init__(self, entries=22,*, start=24, **kwargs):
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