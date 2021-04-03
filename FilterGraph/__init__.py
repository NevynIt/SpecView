"""
Classes to be created
Filter:
    has a number of input ports - callable object or bound property
    has a number of output ports - method, callable object or bound property
    has a number of parameters
    Serialize(target)
    DeSerialize(source)

Port is a callable with args(t0, timerange):
        get enough from the inputs to be able to create the output (it could get less than what it needs)
        elaborate
        return a block containing timerange or less data (in case not enough data were available)

SignalBlock:
    data: a 3D numpy matrix with shape [signal channels, time, freq/tone] and values between 0 and 1
    domain: "freq" or "tone" (or maybe others in the future)
    bounds: a 3x2 matrix with min/max for each dimension. e.g. bounds[0,0] is min channel number, bounds[2,0] is min time, bounds[3,1] is max frequency

FilterGraph(Filter):
    Contains a set of filters



"""
__all__= ["Filters"]

