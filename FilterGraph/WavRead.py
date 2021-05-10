import class_definition_helpers as cdh #class definition helpers

import numpy as np
import wave, numbers
import itertools

from .ndfield import *
from .sampled_axis import sampled_axis

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
        time = sampled_axis()
        time.unit = "s"
        time.axis_domain = domain(0, params.nframes/params.framerate, 1/params.framerate)
        time.fill_mode = "zeros"

        channels = identity_axis()
        channels.axis_domain = domain(0,params.nchannels,1)
        return (time, channels)

    @property
    def dtype(self):
        if self.params == None:
            return np.int16
        return np.dtype(f"<i{self.params.sampwidth}")

    @cdh.indexable
    def samplespace(self, i):
        t, c = i #unpack the tuple

        #t is a set of unique and sorted indexes, as provided by complex_interp
        nframes = self.shape[0]
        nchannels = self.shape[1]
        if isinstance(t, slice):
            step = t.step or 1
            if step != 1:
                raise IndexError("WavReader does not support direct resampling, consider using an interpolator")
            if step > 0:
                start = t.start or 0
                stop = t.stop or nframes
            elif step < 0:
                warnings.warn("maybe incorrect, boundaries might be wrong")
                start = t.start or (nframes - 1)
                stop = t.stop or (0 - 1)
            t = np.arange(start,stop,step)
        elif isinstance(t, numbers.Number):
            t = np.array(t)
        
        if isinstance(t, np.ndarray):
            res = np.zeros( (0,nchannels), dtype = self.dtype)
            if len(t)==0:
                return res
            t = t.astype(np.int_)

            bs = self.block_size
            with wave.open(self.filename, "r") as w:
                pos = 0
                while len(t) > 0:
                    pos += t[0]
                    t -= t[0]
                    frames = max(t[t<bs])+1
                    t = t[t>=frames]
                    w.setpos(pos)
                    data = w.readframes(frames)
                    data = np.frombuffer(data, f"<i{self.params.sampwidth}").reshape( (frames, self.params.nchannels) )
                    res = np.concatenate( (res, data) )
            return res[:,c]
        
        raise NotImplementedError