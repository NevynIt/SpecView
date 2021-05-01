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

    def expand_key(self, key):
        return ndfield.expand_key(self, key, constrain_bounds=False, force_ascending=True)

    def samplespace(self, i):
        t, c = i #unpack the tuple
        nframes = self.shape[0]
        nchannels = self.shape[1]
        if isinstance(t, slice):
            start = max(t.start, 0)
            stop = min(t.stop, nframes)

            tmp = self.read(start, stop-start)
            pre = np.zeros((max(0,-t.start),nchannels),dtype = self.dtype)
            post = np.zeros((max(0,t.stop - nframes),nchannels),dtype = self.dtype)
            tmp = np.concatenate( (pre,tmp,post) )
            tmp = tmp[::t.step]
            tmp = tmp[:,c]
            return tmp
        elif isinstance(t, numbers.Number):
            if t < 0 or t>=nframes:
                return np.zeros((nchannels,),dtype = self.dtype)
            else:
                tmp = self.read(t, 1)
                tmp = tmp[c]
                return tmp
        else:
            t = np.asanyarray(t)
            assert len(t.shape == 1)

            start = max(np.min(t), 0)
            stop = min(np.max(t)+1, nframes)

            tmp = self.read(start, stop-start)
            inrange = (t>=0) & (t<nframes)
            tm2 = np.zeros((t.shape[0],nchannels), dtype = self.dtype)
            tmp2[inrange] = tmp[t[inrange]]
            tmp = tmp2[:,c]
            return tmp