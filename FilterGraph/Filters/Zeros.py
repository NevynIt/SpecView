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