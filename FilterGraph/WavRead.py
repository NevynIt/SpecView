import class_definition_helpers as cdh #class definition helpers

import numpy as np
import wave, numbers
import itertools

def prockey(key, shape):
    if isinstance(key,numbers.Integral):
        key = (key,)
    if not isinstance(key,tuple) or len(key) > len(shape):
        return None
    res = []
    for k, s in itertools.zip_longest(key, shape):
        if isinstance(k,numbers.Integral):
           k = slice(k,k+1,1)
        if not isinstance(k, slice):
            return None
        res.append(slice(*k.indices(s)))
    return res

class WavReader:
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

    @property
    def shape(self):
        if self.params == None:
            return (0,0)
        return (self.params.nframes, self.params.nchannels)

    @property
    def dtype(self):
        if self.params == None:
            return np.int16
        return np.dtype(f"<i{self.params.sampwidth}")

    def read(self,pos,frames):
        if frames <= 0:
            return np.zeros( (0,self.params.nchannels) )

        with wave.open(self.filename, "r") as w:
            w.setpos(pos)
            data = w.readframes(frames)
            return np.frombuffer(data, f"<i{self.params.sampwidth}").reshape( (frames, self.params.nchannels) )

    def __getitem__(self, key):
        if self.params == None:
            if isinstance(key, slice):
                if key.start == None and key.stop == None:
                    return np.zeros( (0,0), dtype=np.int16 )
            elif isinstance(key, tuple):
                if len(key) == 2 and \
                        isinstance(key[0], slice) and isinstance(key[1], slice) and \
                        key[0].start == None and key[0].stop == None and \
                        key[1].start == None and key[1].stop == None:
                    return np.zeros( (0,0), dtype=np.int16 )
            else:
                raise KeyError(f"Invalid key {key}")
        else:
            if isinstance(key,numbers.Integral):
                if key >=0 and key <self.shape[0]:
                    return self.read(key,1)
            elif isinstance(key, slice):
                key = slice(*key.indices(self.shape[0]))
                if key.start >=0 and key.stop <= self.shape[0]:
                    tmp = self.read(key.start,key.stop-key.start)
                    return tmp[::key.step]
            elif isinstance(key, tuple):
                if len(key) == 2:
                    
            else:
                raise KeyError(f"Invalid key {key}")
        raise IndexError(f"index {key} is not valid or out of bounds")

    def __array__(self, dtype=None):
        if self.params == None:
            return np.zeros( (0,0), dtype=np.int16 )
        if dtype == None:
            dtype = self.dtype
        
        return self[:]
        