from ..Filter import Filter
from ..Block import Block
import numpy as np
import wave

class WavReader(Filter):
    auto_attributes = {
        "m_filename": "",
        "open_filename": "",
        "_reader": None
        }

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
    def p_framerate(self):
        self.open(self.p_filename)
        if self.open_filename == "":
            return None
        return self._reader.getframerate()

    @property
    def p_frames(self):
        self.open(self.p_filename)
        if self.open_filename == "":
            return None
        return self._reader.getnframes()

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
        return self._reader.tell()
    
    @property
    def p_EOF(self):
        if self.open_filename == "":
            return None
        return self._reader.tell() == self._reader.getnframes()

    def p_out(self, frames = None, pos = None):
        self.open(self.p_filename)
        if self.open_filename == "":
            return None

        tmp = Block()
        tmp.p_domain = Block.Domains.TIME
        tmp.p_source_range = (0, self.p_frames)

        framerate = self._reader.getframerate()
        channels = self._reader.getnchannels()
        tmp.p_framerate = framerate

        if frames == None:
            tmp.p_data = np.zeros( (channels,0,1) )
            return tmp
        
        tmp.p_data = np.zeros( (channels,frames,1) )
        if pos == None:
            pos = self.p_pos

        if pos+frames >= self.p_frames:
            tmp.p_EOF = True

        if pos < 0:
            skip = -pos
            toread = frames-skip
        else:
            skip = 0
            toread = frames
            if pos != self.p_pos:
                self._reader.setpos(pos)
        
        if toread > 0:
            wavdata = self._reader.readframes(toread)
            samplewidth = self._reader.getsampwidth()
            sampleformat = f"<i{samplewidth}"
            data = np.frombuffer(wavdata, sampleformat).reshape( (1, -1, channels) ).T.astype(np.float32) / (2**15)
            tmp.p_data[:,skip:skip+data.shape[1],:] = data
        
        return tmp

class WavWriter(Filter):
    auto_attributes = {
        "p_domain": Block.Domains.TIME,
        "m_filename": "",
        "open_filename": "",
        "_writer": None,
        "m_in": None
    }

    cached_props = {
        "p_in_params": lambda self, name: None if self.p_in == None else self.p_in()
    }

    @property
    def p_frames(self):
        if self.p_in_params == None:
            return None
        return self.p_in_params.p_source_frames
    
    @property
    def p_channels(self):
        if self.p_in_params == None:
            return None
        return self.p_in_params.p_channels
    
    @property
    def p_framerate(self):
        if self.p_in_params == None:
            return None
        return self.p_in_params.p_framerate
    
    def open(self, filename):
        if filename == self.open_filename:
            return

        self.close()
        if filename != "":
            self._writer = wave.open(filename,"w")
            self._writer.setcomptype("NONE", "not compressed")
            self._writer.setnchannels(self.p_channels)
            self._writer.setsampwidth(2) #always save as signed int16
            self._writer.setframerate(self.p_framerate)
            self._writer.setnframes(self.p_frames - self.p_in_params.p_end)

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
        return self._writer.tell()

    def flush(self, frames):
        self.open(self.p_filename)
        if not self.p_in is None:
            src = self.p_in(frames)
            assert src.p_domain == Block.Domains.TIME
            assert src.p_framerate == self._writer.getframerate()
            assert src.p_channels == self._writer.getnchannels()
            assert src.p_frequency_bins == 1
            self._writer.writeframesraw( (src.p_data*(2**15)).astype(np.int16).T.tobytes() )