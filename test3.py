from FilterGraph.WavRead import WavReader
from FilterGraph.scipy_interp import scipy_interpolator
import numpy as np

wr = WavReader()
print(f"{wr[:].shape=}")
wr.filename = r"res\morn2.wav"
print(f"{wr[:].shape=}")

smp0 = wr[0]
onesecs = wr.coordspace[0:1]
halfrate_left = wr[0:44100:2,0]
dblrate_swap = wr[0:44100:0.5,[1,0]]
wacky = wr[0:44100:0.32,[0,1,0,1,0,0,0,1,1]]

pre = wr[-10:10:0.5]
stop = wr.axes[0].index_domain.stop
post = wr[stop-10: stop+10: 2, 1]

wr.axes[0].interpolator = scipy_interpolator()
lin = wr[0:44100:0.5,[1,0]]
print(lin-dblrate_swap)

fft = np.fft.rfft(lin,axis=0)
print(fft)