import class_definition_helpers as cdh #class definition helpers

import numpy as np
import wave, numbers
import itertools

from .ndfield import *

def prockey(key, shape):
    if isinstance(key,numbers.Integral) or isinstance(key,slice):
        key = (key,)
    if not isinstance(key,tuple) or len(key) > len(shape):
        return None
    res = []
    for k, s in itertools.zip_longest(key, shape, fillvalue=slice(None)):
        if isinstance(k,numbers.Integral):
           k = slice(k,k+1,1)
        if not isinstance(k, slice):
            return None
        res.append(slice(*k.indices(s)))
    return res

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

    # shape = props.cached(params, getter=ndfield.shape.getter)

    def read(self,pos,frames):
        if frames <= 0:
            return np.zeros( (0, self.shape[1]) )

        with wave.open(self.filename, "r") as w:
            w.setpos(pos)
            data = w.readframes(frames)
            return np.frombuffer(data, f"<i{self.params.sampwidth}").reshape( (frames, self.params.nchannels) )

    def samplespace(self, i):
        i1 = self.axes[0].index_domain.intersect(i)
        #TODO: continue from here
        
        raise NotImplementedError
        newkey  = prockey(key, self.shape)
        if newkey == None:
            raise IndexError(f"index {key} is not valid or out of bounds")
        tmp = self.read(newkey[0].start,newkey[0].stop-newkey[0].start)
        return tmp[::newkey[0].step,newkey[1]]