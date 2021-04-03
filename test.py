from FilterGraph import *
import numpy as np
import time

def testWav():
    from FilterGraph.Filters.Wav import WavReader, WavWriter
    from FilterGraph.Filters.Resample import Resample

    wr = WavReader()
    wr.p_filename = r"res\Pirates.wav"

    rs = Resample(wr.p_out)
    rs.p_framerate = 22050

    ww = WavWriter(rs.p_out)
    ww.p_filename = r"out\Pirate22050.wav"

    t0 = time.time()
    while not wr.p_EOF:
        ww.flush(1024)
    print(ww.p_pos, time.time() - t0)
    
    ww.close()

testWav()