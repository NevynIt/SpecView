import class_definition_helpers as cdh

import numpy as np
import wave, numbers

from FilterGraph.ndfield import *
from FilterGraph.axes import axis_info, linear_axis_info

class WavReader(ndfield):
    props = cdh.property_store()
    filename = props.bindable()
    block_size = cdh.default(15*1024*1024)

    @props.cached(filename)
    def params(self):
        try:
            with wave.open(self.filename, "r") as w:
                p = w.getparams()
                if p.comptype == "NONE":
                    return p
                else:
                    return None
        except Exception as e:
            return None

    @props.cached(params)
    def axes(self):
        params = self.params
        if params == None:
            params = wave._wave_params(1,1,1,0,"NONE","")
        self.time = linear_axis_info(params.nframes, step=1/params.framerate, unit="s")
        self.channels = linear_axis_info(2)
        return (self.time, self.channels)

    @property
    def dtype(self):
        if self.params == None:
            return np.int16
        return np.dtype(f"<i{self.params.sampwidth}")
    
    def __getitem__(self, key):
        t, c = self.expand_ellipsis(key) #unpack the tuple
                
        nframes = self.shape[0]
        nchannels = self.shape[1]

        t = self.ensure_int_indexes(t, 0)
        c = self.ensure_int_indexes(c, 1)

        if isinstance(t, slice):
            #FIXME: optimise this code, use the fact we are working with a slice! Moreover, it does not work for step < 0
            t = np.arange(t.start,t.stop,t.step)
        elif isinstance(t, numbers.Number):
            t = np.array([t])
        
        if isinstance(t, np.ndarray):
            res = np.zeros( (0,nchannels), dtype = self.dtype)
            if len(t)==0:
                return res

            t1, inv = np.unique(t, return_inverse=True) #TODO: this could be skipped if we know it's sorted and without duplicates anyway
            if t1[0]<0 or np.searchsorted(t1,self.params.nframes) != len(t1):
                raise IndexError("Out of bounds")

            bs = self.block_size
            with wave.open(self.filename, "r") as w:
                pos = 0
                while len(t1) > 0:
                    pos += t1[0]
                    t1 -= t1[0]
                    indices = np.searchsorted(t1,bs)
                    frames = t1[indices-1]+1
                    w.setpos(pos)
                    data = w.readframes(frames)
                    data = np.frombuffer(data, f"<i{self.params.sampwidth}").reshape( (frames, self.params.nchannels) )
                    data = data[t1[:indices]]
                    res = np.concatenate( (res, data) )
                    t1 = t1[indices:]
            res = res[inv]

            return res[:,c]
        
        raise NotImplementedError