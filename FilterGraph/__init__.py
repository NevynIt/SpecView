"""
Classes:
    Axis
        name -> channel, time, frequency, power (maybe others in the future)
        entries -> number of entries available in the axis, can be 0 to say no entries are available (read always returns an empty signal, write always returns 0) or -1 to say the axiss is not constrained
        start -> the value at the left of index 0 in this axis
        end -> the value to the right of the last index in this axis
        scale -> linear or log, used to calculate the values right or left of any other index

    Descriptor
        is a list of axes
        the last represents the meaning of the stored value itself
        axes names should not be repeated

    Signal
        is a multi dimensional array, possibly a numpy array, with axes defined as in the descriptor

    Source
        [sources] - defined slots for source(s), if any, class dependent
        read(entries, advance) -> Signal, pos (as it would be returned by tell(), used to identify EOF)
            starting from the current position (returned by tell()), reads what it needs from the given sources and returns a signal as big as possible but not bigger than "entities"
            entities: tuple of ints 
                can be empty, a single number or a list/tuple (a single number is considered in a tuple of size 1, None is considered an empty tuple)
                the values in the tuple limit how much information is returned in each of the axis (in the order specified in the descriptor)
                any value that is None and all the axes beyond the lenght of the tuple are left unbounded
            advance: tuple of bool, default is (True, )
                can be empty, single value or tuple/list of bool
                automatically moves the position after the entries returned, for each of the axes for which a value of True was reported
            This is the most complete implementation, subclasses can implement less but should raise exceptions if called with requests they cannot support

        descriptor - returns a descriptor with information about what kind of signal will be sent with the current setup (in terms of connections and parameters)
        seek(pos, absolute = True) 
            sets the current position to pos
                - also seeks on the sources to get to the required position
            pos: tuple of ints
                similar to read, sets the position on one or all the axes, axis for which None has been passed, the position is unchanged
        tell() -> pos (tuple along all axes)
        @property position - equivalent to using seek and tell

    Sink
        [sinks] - defined slots for sink(s), if any, class dependent
        write(Signal, advance) -> number of frames processed, for each axis
            elaborates the signal provided and passes it on to the registered sinks using write on them
            advance
                see the description for Sources, it works the same way
        descriptor - returns a descriptor with information about the kind of data expected from the write function
        seek(pos) - also seeks on the sinks to prepare them to the required position
        tell() -> pos
        @property position - equivalent to using seek and tell

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
        descriptor -> returns a descriptor with information about the kind of data expected from the pump function
        pump(entries)
            reads information from the sources, transforms it, and sends it to the sinks
            entries is referred to the number of entries (see Source above) in accordance with the descriptor
        seek(pos)
        tell() -> pos
        @property position

"""
from uti.autoinit import autoinit
__all__= ["Filters"]
