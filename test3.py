# from FilterGraph.WavRead import WavReader

# wr = WavReader()
# print(f"{wr[:].shape=}")
# wr.filename = r"res\morn2.wav"

# t = wr.axes.time
# pass
# print(f"{wr[:].shape=}")
# print(f"{wr[1].shape=}")
# print(f"{wr[0:50].shape=}")
# print(f"{wr[:,1].shape=}")
# print(f"{wr[0:50:5,0].shape=}")

from FilterGraph.ndfield import *

a1 = linear_sampled_axis()
a1.axis_domain = domain(0,10000,2)
a2 = linear_sampled_axis()
a2.axis_domain = domain(100,200,0.5)

print(expand_indexes((23,slice(120,150,1)), (a1.index_domain,a2.index_domain)))