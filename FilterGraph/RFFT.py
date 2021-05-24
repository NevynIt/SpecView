from FilterGraph.ndtransform import ndtransform
import class_definition_helpers as cdh
from FilterGraph.ndfield import ndfield
from FilterGraph.ndtransform import ndtransform
from FilterGraph.axes import domain
from FilterGraph.sampled_axis import sampled_axis
import contextvars
import numpy as np

desired_freqs = contextvars.ContextVar("desired_freqs")
inverse = contextvars.ContextVar("inverse")

class RFFT(ndtransform):
    def __init__(self, wrapped: ndfield, axis = 0, window = None, spacing = None):
        super().__init__(wrapped)
        self.axis = axis
        if window is None:
            window = np.hanning(1024)
        self.window = window
        if len(window.shape)!= 1:
            raise ValueError("Window must be 1-dimensional")
        if len(window) == np.inf:
            raise ValueError("Infinite windows not supported")
        if not spacing:
            spacing = self.wrapped.axes[self.axis].axis_domain.step
        if not spacing:
            raise ValueError("Undefined sample spacing for source field")
        self.spacing = spacing
        freq = sampled_axis()
        freq.unit = "Hz"
        freq.axis_domain = domain(0,(int(self.window.size/2)+1)/(self.window.size*self.spacing),1/(self.window.size*self.spacing))
        self.freq_axis = freq

    @property
    def axes(self):
        return tuple(self.wrapped.axes) + (self.freq_axis,)

    @property
    def dtype(self):
        return np.complex_

    def identify_indexes(self, di):
        di = list(self.expand_ellipsis(di))
        di1 = self.to_index_array(di[self.axis], self.axis)
        sampler = (np.arange(self.window.size)-int(self.window.size/2)) #FIXME: this assumes that the source axis is a sampled axis
        ind = np.repeat(di1,sampler.size).reshape( (di1.size, sampler.size) )
        ind += np.repeat(sampler,di1.size).reshape( (sampler.size, di1.size) ).T
        ind = ind.flatten()
        ind, inv = np.unique(ind, return_inverse=True)
        inverse.set(inv)
        di[self.axis] = ind
        desired_freqs.set(di[-1])
        return tuple(di[:-1])

    def calculate_values(self, rv):
        df = desired_freqs.get()
        inv = inverse.get()
        rv = np.take(rv,inv,self.axis)
        newshape = list(rv.shape)
        newshape[self.axis] //= self.window.size
        newshape = [self.window.size,] + newshape
        rv = rv.reshape( newshape ) * self.window[:,np.newaxis,np.newaxis]
        rv = np.fft.rfft(rv,axis = 0)
        rv = rv[df]
        rv = np.moveaxis(rv,0,-1)
        return rv
        