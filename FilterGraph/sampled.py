from typing import Tuple
from FilterGraph.ndfield import ndfield
from FilterGraph.axis_transform import axis_transform
from FilterGraph.axes import axis_info
import numpy as np
import contextvars

# class sampled(axis_transform):
#     def __init__(self, wrapped: ndfield, domains: Tuple(axis_info)):
#         "domains are the axis_info describing the samplers applied to each axis"
#         super().__init__(wrapped, axes=axes)