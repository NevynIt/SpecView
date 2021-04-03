from FilterGraph import *
import numpy as np
import time

def testWav():
    from FilterGraph.Filters.Wav import WavReader, WavWriter
    from FilterGraph.Filters.Resample import Resample

    wr = WavReader()
    wr.p_filename = r"res\Pirates.wav"

    rs = Resample()
    rs.bind_props("p_in", wr, "p_out")
    rs.p_framerate = 22050

    ww = WavWriter()
    ww.bind_props("p_in", rs, "p_out")
    ww.p_filename = r"out\Pirate22050.wav"

    t0 = time.time()
    while not wr.p_EOF:
        ww.flush(1024)
    print(ww.p_pos, time.time() - t0)
    
    ww.close()

    rs.p_framerate = 3000
    ww.p_filename = f"out\\Pirate{rs.p_framerate}.wav"

    #reset the stream
    wr.p_out(0,0)

    t0 = time.time()
    while not wr.p_EOF:
        ww.flush(1024)
    print(ww.p_pos, time.time() - t0)

testWav()