from ..Filter import Filter
from ..Block import Block
import numpy as np
import nnresample
import scipy.interpolate
import scipy.signal
import enum

class Resample(Filter):
    class Methods(enum.Enum):
        NUMPY = 1
        NNRESAMPLE = 2
        SCIPY_INTERP = 3
        SCIPY_RESAMPLE = 4

    auto_attributes = {
        "p_method": Methods.SCIPY_INTERP,
        "p_interp_kind": "linear",
        "m_resolution": np.array( [44100, np.nan] ),
        "m_in": None
        }
    
    def __init__(self, input = None):
        Filter.__init__(self)
        self.p_in = input

    def p_out(self, t0, t1):
        if self.p_in == None:
            return None
        
        tmp = Block()
        src = self.p_in(t0,t1)
        tmp.domain = src.domain
        tmp.resolution[0] = self.p_resolution[0]
        tmp.resolution[1] = src.resolution[1]
        
        tmp.bounds = src.bounds
        if self.p_method == Resample.Methods.NNRESAMPLE:
            tmp.data = nnresample.resample(src.data,self.p_resolution[0],src.resolution[0],1)
        
        elif self.p_method == Resample.Methods.SCIPY_INTERP:
            nsamples = int(tmp.resolution[0]*(tmp.bounds[0,1]-tmp.bounds[0,0]))
            x = np.mgrid[0: 1: 1/nsamples]
            xp = np.mgrid[0: 1: 1/src.data.shape[1]]
            interpolator = scipy.interpolate.interp1d(xp, src.data, axis = 1, copy = False, kind=self.p_interp_kind)
            tmp.data = interpolator(x)
        
        elif self.p_method == Resample.Methods.SCIPY_RESAMPLE:
            nsamples = int(tmp.resolution[0]*(tmp.bounds[0,1]-tmp.bounds[0,0]))
            tmp.data = scipy.signal.resample(src.data,nsamples,axis=1)

        elif self.p_method == Resample.Methods.NUMPY:
            tmp.data = np.zeros( (self.p_channels, int(tmp.resolution[0]*(tmp.bounds[0,1]-tmp.bounds[0,0])), int(tmp.resolution[1]*(tmp.bounds[1,1]-tmp.bounds[1,0])) ) )
            x = np.mgrid[0: 1: 1/tmp.data.shape[1]]
            xp = np.mgrid[0: 1: 1/src.data.shape[1]]
            for channel in range(tmp.data.shape[0]):
                for freq in range(tmp.data.shape[2]):
                    tmp.data[channel,:,freq] = np.interp(x,xp,src.data[channel,:,freq])

        return tmp