import class_definition_helpers as cdh
from FilterGraph.ndfield import ndfield
import contextvars

class ndtransform(ndfield):
    props = cdh.property_store()

    #TODO: make the thing cdh.reactive to support buffering
    def __init__(self, wrapped: ndfield):
        super().__init__()
        self.wrapped = wrapped

    wrapped = props.reactive( None )

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