from ..Filter import Filter
from ..Block import Block
import wave
import numpy as np

class WavReader(Filter):
    auto_attributes = {"m_filename": "", "open_filename": "", "_reader": None}

    def close(self):
        """Close the wav file."""
        if not self._reader is None:
            self._reader.close()
            self._reader = None
        self.open_filename = ""

    def open(self, filename):
        if filename == self.open_filename:
            return

        self.close()
        if filename != "":
            self._reader = wave.open(filename,"rb")
            if self._reader.getcomptype() != "NONE":
                raise Exception(f"Compressed WAV not supported opening '{filename}'")
        self.open_filename = filename
    
    @property
    def p_domain(self):
        return Block.Domains.TIME
    
    @property
    def p_resolution(self):
        self.open(self.p_filename)
        if self.open_filename == "":
            return None
        return np.array( [self._reader.getframerate(), np.nan] )

    @property
    def p_bounds(self):
        self.open(self.p_filename)
        if self.open_filename == "":
            return None
        return np.array( [[0,self._reader.getnframes()/self._reader.getframerate()],[np.nan,np.nan]] )

    @property
    def p_channels(self):
        self.open(self.p_filename)
        if self.open_filename == "":
            return None
        return self._reader.getnchannels()

    @property
    def p_pos(self):
        if self.open_filename == "":
            return None
        return self._reader.tell()/self._reader.getnframes()
    
    @property
    def p_EOF(self):
        if self.open_filename == "":
            return None
        return self._reader.tell() == self._reader.getnframes()

    def p_out(self, t0, t1):
        self.open(self.p_filename)
        tmp = Block()
        tmp.domain = Block.Domains.TIME

        if self.open_filename == "":
            return None

        framerate = self._reader.getframerate()
        channels = self._reader.getnchannels()
        tmp.resolution = np.array( [framerate, np.nan] )

        if t1<=t0:
            return None

        tmax = self._reader.getnframes() / framerate
        if t1 >= tmax:
            t1 = tmax
            tmp.EOF = True

        tmp.data = np.zeros( (channels,int((t1-t0)*framerate),1) )
        tmp.bounds = np.array([[t0,t1],[np.nan,np.nan]])

        if t1 <= 0:
            return tmp

        if t0 < 0:
            blanks = int(-t0*framerate)
        else:
            blanks = 0
            self._reader.setpos(int(t0*framerate))
        
        toread = int((t1-t0)*framerate)-blanks
        frames = self._reader.readframes(toread)
        samplewidth = self._reader.getsampwidth()
        sampleformat = f"<i{samplewidth}"
        tmp.data[:,blanks:,:] = np.frombuffer(frames, sampleformat).reshape( (1, -1, channels) ).T.astype(np.float32) / (2**15)
        return tmp

class WavWriter(Filter):
    auto_attributes = {
        "p_domain": Block.Domains.TIME,
        "m_bounds": np.array( [[-np.Infinity,np.Infinity],[np.nan,np.nan]] ),
        "m_resolution": np.array( [np.nan, np.nan] ),
        "m_channels": np.nan,
        "m_filename": "",
        "open_filename": "",
        "_writer": None,
        "m_in": None
        }

    def open(self, filename):
        if filename == self.open_filename:
            return

        self.close()
        if filename != "":
            self._writer = wave.open(filename,"w")
            self._writer.setcomptype("NONE", "not compressed")
            self._writer.setnchannels(self.p_channels)
            self._writer.setsampwidth(2) #always save as signed int16
            self._writer.setframerate(self.p_resolution[0])
            nframes = (self.p_bounds[0,1]-self.p_bounds[0,0])*self.p_resolution[0]
            if nframes < np.Infinity:
                self._writer.setnframes(int(nframes))

        self.open_filename = filename

    def close(self):
        if not self._writer is None:
            self._writer.close()
            self._writer = None
        self.open_filename = ""

    @property
    def p_pos(self):
        if self.open_filename == "":
            return 0
        return self._writer.tell()/self.p_resolution[0]

    def flush(self, t):
        self.open(self.p_filename)
        if not self.p_in is None:
            src = self.p_in(self.p_pos, self.p_pos + t)
            assert src.domain == Block.Domains.TIME
            assert src.resolution[0] == self.p_resolution[0]
            assert src.data.shape[0] == self.p_channels
            assert src.data.shape[2] == 1
            self._writer.writeframesraw( (src.data*(2**15)).astype(np.int16).T.tobytes() )