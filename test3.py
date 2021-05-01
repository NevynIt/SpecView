from FilterGraph.WavRead import WavReader

wr = WavReader()
print(f"{wr[:].shape=}")
wr.filename = r"res\morn2.wav"
print(f"{wr[:].shape=}")

smp0 = wr[0]
onesecs = wr.coordspace[0:1]
halfrate_left = wr[0:44100:2,0]
dblrate_swap = wr[0:44100:0.5,[1,0]]
wacky = wr[0:44100:0.32,[0,1,0,1,0,0,0,1,1]]

pass