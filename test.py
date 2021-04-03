from FilterGraph import *
import numpy as np
import time

def testBindable():
    from FilterGraph.Filter import Filter

    class dummy:
        def __init__(self):
            self.a = 5
            self.b = 8
        
        @property
        def prop_a(self):
            return self.a
        
        @prop_a.setter
        def prop_a(self, value):
            self.a = value

    d = dummy()
    f1 = Filter()
    f2 = Filter()

    f1.bind_property("p_a",d,"a")
    f1.bind_property("p_propa",d,"prop_a")

    f2.bind_property("p_a", f1, "p_a")
    f2.bind_property("p_propa",f1,"p_propa")

    print(f2.p_a)
    print(f2.p_propa)
    f2.p_propa = 23
    print(d.prop_a)

def testWav():
    from FilterGraph.Filters.Wav import WavReader, WavWriter
    from FilterGraph.Filters.Resample import Resample

    wr = WavReader()
    wr.p_filename = r"res\Pirates.wav"

    rs = Resample()
    rs.p_resolution[0] = 22050
    rs.p_in = wr.p_out

    ww = WavWriter()
    ww.bind_props(["p_resolution"], rs)
    ww.bind_props(["p_channels","p_bounds"], wr)
    ww.p_in = rs.p_out
    ww.p_filename = r"out\Pirate22050.wav"

    t0 = time.time()
    while not wr.p_EOF:
        ww.flush(20)
    print(ww.p_pos, time.time() - t0)
    
    ww.close()

testWav()