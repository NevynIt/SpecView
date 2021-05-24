from FilterGraph import extended
from FilterGraph.WavRead import WavReader
from FilterGraph.extended import extended
from FilterGraph.RFFT import RFFT
import numpy as np
import time

wr = WavReader()
wr.filename = r"res\morn2.wav"

wr = RFFT(extended(wr, mode="repeat",axes=0),window=np.hamming(2**15))
t0 = time.time()
a = wr[0:44100*200:1100]
print(a.shape)
print(time.time() - t0)