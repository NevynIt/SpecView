from ..Filter import Filter
from ..Block import Block
import numpy as np
import scipy.interpolate
import scipy.signal
import enum

class Resample(Filter):
    class Methods(enum.Enum):
        NUMPY = 1
        SCIPY_INTERP = 2
        SCIPY_RESAMPLE = 3

    cached_props = {
        "p_in_params": lambda self,name: None if self.p_in == None else self.p_in()
    }

    auto_attributes = {
        "p_method": Methods.SCIPY_INTERP,
        "p_interp_kind": "linear",
        "p_framerate": 44100,
        "m_in": None
        }
    
    @property
    def p_input_framerate(self):
        if self.p_in_params == None:
            return None
        return self.p_in_params.p_framerate
    
    @property
    def p_ratio(self):
        if self.p_in_params == None:
            return None
        return self.p_framerate/self.p_input_framerate

    def p_out(self, frames = None, pos = None):
        if self.p_in == None:
            return None

        f = self.p_ratio
        if frames == None:
            src = self.p_in_params
        else:
            src = self.p_in(int(frames/f), pos)
        tmp = src.copy()
        #update start, source_range, framerate, data
        tmp.p_framerate = self.p_framerate
        tmp.p_start = int(src.p_start*f)
        tmp.p_source_range = (int(src.p_source_range[0]*f), int(src.p_source_range[1]*f))
        frames = int(src.p_frames*f)

        if frames == 0:
            tmp.p_data = np.zeros( (src.p_channels, 0, src.p_frequency_bins) )
            return tmp

        if self.p_method == Resample.Methods.SCIPY_INTERP:
            x = np.mgrid[0: 1: 1/frames]
            xp = np.mgrid[0: 1: 1/src.p_frames]
            interpolator = scipy.interpolate.interp1d(xp, src.p_data, axis = 1, copy = False, kind=self.p_interp_kind)
            tmp.p_data = interpolator(x)
        
        elif self.p_method == Resample.Methods.SCIPY_RESAMPLE:
            tmp.p_data = scipy.signal.resample(src.p_data,frames,axis=1)

        elif self.p_method == Resample.Methods.NUMPY:
            x = np.mgrid[0: 1: 1/frames]
            xp = np.mgrid[0: 1: 1/src.p_frames]
            tmp.p_data = np.zeros( (self.p_channels, frames, src.p_frequency_bins ) )
            for channel in range(tmp.p_channels):
                for freq in range(tmp.p_frequency_bins):
                    tmp.p_data[channel,:,freq] = np.interp(x,xp,src.p_data[channel,:,freq])

        return tmp