"""
    Split the request into parallel requests on separate threads (not as effective as one may think due to python's GIL)
"""
from ..Filter import Filter
from ..Block import Block
import numpy as np

class Parallel(Filter):
    raise NotImplementedError
    pass