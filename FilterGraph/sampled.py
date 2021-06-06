from typing import Tuple
from FilterGraph.ndfield import ndfield
from FilterGraph.axis_transform import axis_transform
from FilterGraph.axes import axis_info
import numpy as np
import contextvars

class sampled(axis_transform): #FIXME: axis_info has changed!!!!
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
            return axis_info(axis.to_coord(d.origin), axis.step * d.step, d.steps_forwards, d.steps_backwards, d.unit or axis.unit, ("Sampled", ) + d.annotations + axis.annotations)

    def axis_identify_indexes(self, di, axis_n):
        d :axis_info = self.domains[axis_n]
        if d is None:
            return di
        return d.to_coord(di)

# Hierarchy of samplers
# sampler generic - to_coords / to_index (optional)
# linear sampler, log sampler, trigonometric sampler, etc...