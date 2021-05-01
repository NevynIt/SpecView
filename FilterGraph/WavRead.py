import class_definition_helpers as cdh #class definition helpers

import numpy as np
import wave, numbers
import itertools

from .ndfield import *

class WavReader(ndfield):
    props = cdh.property_store()
    filename = props.bindable()

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
        time = linear_sampled_axis()
        time.unit = "s"
        time.axis_domain = domain(0, params.nframes/params.framerate, 1/params.framerate)
        channels = identity_axis()
        channels.axis_domain = domain(0,params.nchannels,1)
        return (time, channels)

    @property
    def dtype(self):
        if self.params == None:
            return np.int16
        return np.dtype(f"<i{self.params.sampwidth}")

    def read(self,pos,frames):
        if frames <= 0:
            return np.zeros( (0, self.shape[1]) )

        with wave.open(self.filename, "r") as w:
            w.setpos(pos)
            data = w.readframes(frames)
            return np.frombuffer(data, f"<i{self.params.sampwidth}").reshape( (frames, self.params.nchannels) )

    def samplespace(self, i):
        t, c = i #unpack the tuple
        if isinstance(t, slice):
            tmp = self.read(t.start, t.stop-t.start)
            tmp = tmp[::t.step]
            tmp = tmp[:,c]
            return tmp
        else:
            tmp = self.read(np.min(t), np.max(t) - np.min(t) + 1)
            tmp = tmp[t,c]
            return tmp