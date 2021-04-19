from FilterGraph.WavRead import WavReader

wr = WavReader()
print(f"{wr[:].shape=}")
wr.filename = r"res\morn2.wav"

print(f"{wr[:].shape=}")
print(f"{wr[1].shape=}")
print(f"{wr[0:50].shape=}")
print(f"{wr[:,1].shape=}")
print(f"{wr[0:50:5,0].shape=}")