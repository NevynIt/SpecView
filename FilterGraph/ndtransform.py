import class_definition_helpers as cdh
from FilterGraph.ndfield import ndfield
import contextvars
import numpy as np
from numbers import Number

class ndtransform(ndfield):
    props = cdh.property_store()

    #TODO: make the thing cdh.reactive to support buffering
    def __init__(self, wrapped: ndfield):
        super().__init__()
        self.wrapped = wrapped

    wrapped = props.reactive()

    @property
    def axes(self):
        return self.wrapped.axes
    
    @property
    def dtype(self):
        return self.wrapped.dtype

    def identify_indexes(self, di):
        return di

    def calculate_values(self, rv):
        return rv

    def __getitem__(self, indexes):
        ctx = contextvars.Context()
        indexes = ctx.run(self.identify_indexes, indexes)
        values = self.wrapped[indexes]
        values = ctx.run(self.calculate_values, values)
        return values

    def to_index_array(self, indexes, axis_n):
        axis = self.wrapped.axes[axis_n]

        if isinstance(indexes, np.ndarray):
            return indexes
        elif isinstance(indexes, Number):
            return np.array(indexes) #TODO: not sure why it was plain number before, it should have been a ndarray
        elif isinstance(indexes, slice):
            domain = axis.index_slice
            step = indexes.step or 1
            if step > 0:
                if indexes.start is None:
                    start = domain.start
                else:
                    start = indexes.start
                if indexes.stop is None:
                    stop = domain.stop
                else:
                    stop = indexes.stop
            elif step < 0:
                # warnings.warn("maybe incorrect, boundaries might be wrong")
                if indexes.start is None:
                    start = domain.stop - domain.step
                else:
                    start = indexes.start
                if indexes.stop is None:
                    stop = domain.start - domain.step
                else:
                    stop = indexes.stop
            return np.arange(start,stop,step)
        else:
            return np.array(indexes)