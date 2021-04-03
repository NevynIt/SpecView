import numpy as np
from ..Filter import Filter
from ..Block import Block

class Zeros(Filter):
    auto_attributes = {
        "m_domain": Block.Domains.TIME,
        "m_bounds": np.array( [[-np.Infinity,np.Infinity],[0,1]] ),
        "m_resolution": np.array( [44100, 1] ),
        "m_channels": 2
        }

    def p_out(self, t0, t1):
        tmp = Block()
        tmp.domain = self.p_domain
        tmp.resolution = self.p_resolution
        tmp.bounds = np.array( ((t0,t1), self.p_bounds[1]) )
        tmp.data = np.zeros( (self.p_channels, int(tmp.resolution[0]*(t1-t0)), int(tmp.resolution[1]*(tmp.bounds[1,1]-tmp.bounds[1,0])) ) )
        return tmp

class ZeroPadding(Filter):
    auto_attributes = {
        "m_in": None
        }
    
    def __init__(self, input = None):
        self.p_in = input

    def p_out(self, t0, t1):
        if self.p_in == None:
            return None

        src = self.p_in(t0,t1)
        if src.bounds[1] < t1:
            padding = int(src.resolution[1]*(t1-src.bounds[0,1]))
            src.data = np.pad(src.data, [(0,0),(0,padding),(0,0)])

        return src