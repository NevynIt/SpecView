from typing import Tuple
from FilterGraph.ndfield import ndfield
from FilterGraph.axis_transform import axis_transform
from FilterGraph.axes import axis_info
import numpy as np
import contextvars

class sampled_axis_info(axis_info):
    def __init__(self, source: axis_info, sampler: axis_info):
        self.source=source
        self.sampler=sampler
    
    @property
    def size(self):
        return self.sampler.size
    
    @property
    def lbound(self):
        return self.sampler.lbound
    
    @property
    def ubound(self):
        return self.sampler.ubound
    
    @property
    def unit(self):
        return self.source.unit
    
    @property
    def annotations(self):
        return ("Sampled",)+ ("(",) + self.sampler.annotations + (")",) + self.source.annotations

    def to_index(self, x):
        return self.sampler.to_index(self.source.to_index(x))
    
    def to_coord(self, x):
        return self.source.to_coord(self.sampler.to_coord(x))

class sampled(axis_transform):
    def __init__(self, wrapped: ndfield, domains: Tuple[axis_info]):
        "domains are the axis_info describing the samplers applied to each axis"
        axes = set()
        for i in range(len(domains)):
            if domains[i] != None:
                axes.add(i)
        # if len(axes) == 0:
        #   warning!
        super().__init__(wrapped, axes=axes)
        self.domains :Tuple[axis_info] = domains + (None, ) * (len(wrapped.axes) - len(domains))
    
    def transform_axis(self, axis: axis_info, i):
        d :axis_info = self.domains[i]
        if d is None:
            return axis
        else:  
            return sampled_axis_info(axis, d)

    def axis_identify_indexes(self, di, axis_n):
        d :axis_info = self.domains[axis_n]
        if d is None:
            return di
        return d.to_coord(di)