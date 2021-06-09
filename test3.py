from FilterGraph.axes import linear_axis_info, log_axis_info
from FilterGraph import extended
from FilterGraph.WavRead import WavReader
from FilterGraph.interpolated import interpolated
from FilterGraph.extended import extended
from FilterGraph.coordspace import coordspace
from FilterGraph.sampled import sampled
from FilterGraph.RFFT import RFFT
import numpy as np
import time

t0 = time.time()
wr = WavReader()
wr.filename = r"res\morn2.wav"

wrfft = RFFT(extended(wr, mode="zeros",axes=0),window=np.hamming(2**12),spacing=1/44100)
la = log_axis_info(80,0,79,scale=np.power(np.power(2,1/12),-49)*440,base=np.power(2,1/12))
wrfftis = sampled(coordspace(interpolated(wrfft,axes=2,mode="linear"),axes=2),domains=(None,None,la))
t1 = time.time()
print(f"setup: {t1-t0}")

b = wrfftis[0:wr.shape[0]:44100/5, 0, 0:80:0.2]
t2 = time.time()
print(f"FFT: {t2-t1}")

b = np.abs(b)
mi = np.min(b)
ma = np.max(b)
b = (b-mi)/(ma-mi) * (2**16)
b = b.astype(np.uint16)
b = np.flip(b,0)
t3 = time.time()
print(f"Tune: {t3-t2}")

import PIL, PIL.Image
#save the file
img = PIL.Image.fromarray(b,"I;16")
img.save(r"out\spec.png")
t4 = time.time()
print(f"Save: {t4-t3}")