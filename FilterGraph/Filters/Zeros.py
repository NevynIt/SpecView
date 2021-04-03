import numpy as np
from ..Filter import Filter
from ..Block import Block

class Zeros(Filter):
    auto_attributes = {
        "m_domain": Block.Domains.TIME,
        "m_framerate": 44100,
        "m_frequency_range": (0, 0),
        "m_frequency_bins": 1,
        "m_channels": 1,
        "p_pos": 0
        }

    def p_out(self, frames = 0, pos = None):
        tmp = Block()
        tmp.p_domain = self.p_domain
        tmp.p_framerate = self.p_framerate
        tmp.p_frequency_range = self.p_frequency_range
        tmp.p_source_range = (0, 0)
        if pos == None:
            pos = self.p_pos
        tmp.p_start = pos
        tmp.p_data = np.zeros( (self.p_channels, frames, self.p_frequency_bins) ) 
        self.p_pos += frames
        return tmp

class ZeroPadding(Filter):
    auto_attributes = {
        "m_in": None
        }
    
    def __init__(self, input = None):
        Filter.__init__(self)
        self.p_in = input

    def p_out(self, frames = 0, pos = None):
        raise NotImplementedError
        
        if self.p_in == None:
            return None

        src = self.p_in(frames,pos)

        # if src.bounds[1] < t1:
        #     padding = int(src.resolution[1]*(t1-src.bounds[0,1]))
        #     src.data = np.pad(src.data, [(0,0),(0,padding),(0,0)])

        return src