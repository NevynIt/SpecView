import class_definition_helpers as cdh
import numpy as np
from numbers import Number
from FilterGraph.ndtransform import ndtransform
from FilterGraph.ndfield import ndfield
import contextvars

axes_to_squeeze = contextvars.ContextVar("axes_to_squeeze")
axis_contexts = contextvars.ContextVar("axis_contexts")

class axis_transform(ndtransform):
    props = cdh.property_store()

    def __init__(self, wrapped: ndfield, axes: int or set = None):
        super().__init__(wrapped)
        if axes == None:
            axes = None
        elif not isinstance(axes, set):
            axes = {axes}
        self.transformation_axes = axes
        #if axes are repeated the transformation will be done multiple times

    wrapped = cdh.inherited_reference()

    @props.cached(wrapped)
    def axes(self):
        tmp = list(self.wrapped.axes)

        ta = self.transformation_axes
        if ta == None:
            ta = set(range(len(tmp)))
        
        for i in ta:
            if i < 0:
                i = len(tmp) - i
            tmp[i] = self.transform_axis(tmp[i])

        return tmp

    def transform_axis(self, axis):
        return axis

    def axis_identify_indexes(self, di, axis_n):
        return di

    def axis_calculate_values(self, rv, axis_n):
        return rv

    def identify_indexes(self, di):
        di = list(self.expand_ellipsis(di))
        a2s = []
        required_indexes = []
        contexts = []

        ta = self.transformation_axes
        if ta == None:
            ta = set(range(len(self.wrapped.axes)))

        for i in ta:
            if i < 0:
                i = len(self.wrapped.axes) - i
            if isinstance(di[i], Number):
                #wrap the scalar indexes, this is needed to make sure samplers work on the right axis
                di[i] = np.array([di[i]])
                a2s.append(i)
            ctx = contextvars.Context()
            contexts.append( (i, ctx ) )
            required_indexes.append(ctx.run(self.axis_identify_indexes, di[i], i))

        axes_to_squeeze.set(a2s)
        axis_contexts.set(contexts)
        return tuple(required_indexes)

    def calculate_values(self, rv):
        #ask each axis in order to perform the interpolation
        contexts = axis_contexts.get()

        for i, ctx in contexts:
            rv = ctx.run(self.axis_calculate_values, rv, i)

        #squeeze the axes where the index was a scalar
        a2s = axes_to_squeeze.get()
        if len(a2s) > 0:
            rv = np.squeeze(rv, a2s)
        
        return rv

    def to_index_array(self, indexes, axis_n):
        axis = self.wrapped.axes[axis_n]

        if isinstance(indexes, np.ndarray):
            return indexes
        elif isinstance(indexes, Number):
            return indexes
        elif isinstance(indexes, slice):
            domain = axis.index_domain
            step = indexes.step or 1
            if step == 0 or step == None:
                raise IndexError
            if step > 0:
                start = indexes.start or domain.start
                stop = indexes.stop or domain.stop
            elif step < 0:
                # warnings.warn("maybe incorrect, boundaries might be wrong")
                start = indexes.start or (domain.stop - domain.step)
                stop = indexes.stop or (domain.start - domain.step)
            return np.arange(start,stop,step)