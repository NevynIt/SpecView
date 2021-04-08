"""
Classes:
    Axis
        name -> channel, time, frequency, power (maybe others in the future)
        entries -> number of entries available in the axis, can be 0 to say no entries are available (read always returns an empty signal, write always returns 0) or -1 to say the axiss is not constrained
        start -> the value at the left of index 0 in this axis
        end -> the value to the right of the last index in this axis
        scale -> linear or log, used to calculate the values right or left of any other index

    Descriptor
        is a list of axes - one of them MUST be time (maybe???)
        the last represents the meaning of the stored value itself
        axes names should not be repeated

    Source
        [sources] - defined slots for source(s), if any, class dependent
        read(nframes) -> Signal - gets what it needs from sources and returns a signalblock of nframes lenght in time - if nframes is none, reads as much as possible from pos
        descriptor - returns a descriptor with information about what kind of signalblock will be sent with the current setup (in terms of connections and parameters)
        seek(pos) - also seeks on the sources to get to the required position
        tell() -> pos
        EOF -> true or false
        @property position

    Sink
        [sinks] - defined slots for sink(s), if any, class dependent
        write(Signal) -> number of frames written
        seek(pos) - also seeks on the sinks to prepare them to the required position
        tell() -> pos
        @property position

    Transform - combination of a source and a sink
        [sources] - defined slots for source(s), if any, class dependent
            when the direction is sink, the object returned from each of these defined sources are sinks
            when the direction is source or pump, these object can and should be bound to sources
            when the direction is none, nothing can be bound
        [sinks] - defined slots for sink(s), if any, class dependent
            when the direction is source, the object returned from each of these defined sinks are sources
            when the direction is sink or pump, these object can and should be bound to other sinks
            when the direction is none, nothing can be bound
        direction -> none, source, sink or pump
        pump(nframes)
        seek(pos)
        tell() -> pos
        @property position

"""
from uti.autoinit import autoinit
__all__= ["Filters"]
