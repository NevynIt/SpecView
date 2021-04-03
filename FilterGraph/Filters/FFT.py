from ..Filter import Filter
from ..Block import Block
import numpy as np

class FFT(Filter):
    auto_attributes = {
        "p_domain": Block.Domains.FREQUENCY,
        "m_resolution": np.array( [16, np.nan] ),
        "m_bins": 2**14,
        "m_channels": 2,
        "m_in": None
        }
    
    def p_out(self, t0, t1):
        raise NotImplementedError
        if self.p_in == None:
            return None
        src = self.p_in(t0,t1)
        assert src.domain == Block.Domains.TIME
        
