from FilterGraph import extended
from FilterGraph.WavRead import WavReader
from FilterGraph.interpolated import interpolated
from FilterGraph.extended import extended
from FilterGraph.coordspace import coordspace

wr = WavReader()
print(f"{wr[:].shape=}")
wr.filename = r"res\morn2.wav"
print(f"{wr[:].shape=}")

smp0 = wr[0]
onesecs = coordspace(wr)[0:1]
iwr = interpolated(wr)
halfrate_left = iwr[0:44100:2,0]
dblrate_swap = iwr[0:44100:0.5, (1,0)]

eiwr = extended(iwr)
dblrate_around = eiwr[-100:100:0.5]
wacky = eiwr[0:44100:0.32, (0,1,0,1,0,0,0,1,1)]

pre = eiwr[-10:10:0.5]

eiwr2 = interpolated(extended(wr, mode="repeat",axes=0), mode="linear",axes=0)
pre2 = eiwr2[-10:10:0.5]

lin = eiwr2[0:44100:0.5,(1,0)]
print(lin-dblrate_swap)

from FilterGraph.RFFT import RFFT
import numpy as np
import time

wrfft = RFFT(extended(wr, mode="repeat",axes=0),window=np.hamming(2**15))
t0 = time.time()
a = wrfft[0:44100*200:1100]
print(a.shape)
print(time.time() - t0)