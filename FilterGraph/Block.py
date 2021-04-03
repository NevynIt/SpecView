import numpy as np
import enum
import copy

class Block:
    class Domains(enum.Enum):
        NONE = 0
        TIME = 1
        FREQUENCY = 2
        TONE = 3

    def __init__(self):
        self.p_domain = Block.Domains(Block.Domains.NONE)
        self.p_EOF = False
        self.p_framerate = 0
        self.p_frequency_range = (0, 0)
        self.p_source_range = (0, 0)
        self.p_start = 0
        self.p_data = np.zeros( (0,0,0) )
    
    def copy(self):
        return copy.copy(self)

    @property
    def p_channels(self):
        return self.p_data.shape[0]
    
    @property
    def p_frames(self):
        return self.p_data.shape[1]
    
    @property
    def p_end(self):
        return self.p_start + self.p_frames

    @property
    def p_frequency_bins(self):
        return self.p_data.shape[2]

    @property
    def p_frame_range(self):
        return (self.p_start, self.p_end)

    @property
    def p_source_frames(self):
        if self.p_source_range == None:
            return None
        return self.p_source_range[1] - self.p_source_range[0]

    @property
    def p_time_range(self):
        if self.p_framerate == 0:
            return None
        return (self.p_frame_range[0]/self.p_framerate, self.p_frame_range[1]/self.p_framerate)