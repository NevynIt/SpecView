import class_definition_helpers as cdh

class axis_info:
    """
    Information about an axis in a ndfield

    Members:
        unit: r/o str
            name of the unit (s, m, Hz, note, ...)
        axis_domain: r/o object
            attributes:
                start: number or -inf
                stop: number or +inf
                    define the boundaries as in a slice object
                step: number or None
                    the gap between valid values for discrete domains
                    1/sampling_rate for sampled domains
                    None for continuous domains where all values are valid
                discrete: bool
                    True for discrete domains
                    False for continuous domains
        index_domain:
            same as axis_domain, but referred to the codomain of the to_index function
        to_index(coordinates, rounding = None):
            arguments
                coordinates: number, slice, iterable with numbers
                rounding: str or None
                    if the domain is sampled or discrete, uses one of the following
                        strategies to round the coordinates to the closest valid one
                    None - use the default for the axis
                    floor - always return the closest, but lower, index
                    ceil - always return the closest, but higher, index
                    round - always return the closest (lower or higher) index
                    throw - throw an exception if a exact match cannot be found
                    exact - no rounding is done
                        may throw an exception for discrete axes
                        may return invalid indexes for sampled axes
            returns the index(es) to be used in the underlying logical ndarray to get the data
        from_index(indexes, rounding = None):
            inverse function, there is no guarantee the mapping is bidirectional
        annotations: tuple of strings
            could be: linear, logarithmic, monotonic, exponential, period=xxx, ...

        mapped: get/set bool
            default = False
            gets or defines the behavior of __getitem__ in the ndfield
            True - getitem expects coordinates in the axis domain
            False - getitem expects indexes in the underlying logical ndarray
        rounding: get/set str
            the default rounding used in __getitem__ (both here and in the main object if mapped)
        __getitem__(coordinates):
            returns to_index(coordinates)
    """
    unit = cdh.property_store.constant("None")

class ndfield:
    """
    N-Dimensional field, mapping the coordinates in a space to either scalars, vectors or objects
    conceptual extension of np.ndarray, with arbitrary axes (not just ints from 0)

    Must have:
        shape 
            tuple of lenghts, one per dimension
            calculated with stop-start for each axis, depends on axes[:].mapped
        
        axes: object
            Members
                __getitem__(n: int)
                    returns the axis_info as defined above
    """
    props = cdh.property_store()

    @cdh.autocreate
    class axes:
        props = cdh.property_store()
        parent = cdh.autocreate.parent_reference()

        def __getitem__(self, key):
            raise NotImplementedError

    @property
    def shape(self):
        raise NotImplementedError
    
    def __getitem__(self, coords):
        '''
        arguments
            coords can be a (tuple of) value or slices, which will be converted to indexes
            using the functions to_index() defined in axes to get the actual data
        '''
        raise NotImplementedError

    def get_mapped_view(self, map_axes = None):
        """
        Returns a linked r/o view to the ndfield where
        axes[...].mapped and .rounding can be modified to access the data in a different way
        map_axes can be set to a tuple of bool to get the axes mapped already
        """
        raise NotImplementedError

