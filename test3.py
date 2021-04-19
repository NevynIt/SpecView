from FilterGraph.WavRead import WavReader

wr = WavReader()
wr.filename = r"res\morn2.wav"
print(wr.params)
print(wr.shape)
print(wr.__array__())
wr[1:2]