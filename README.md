# Dependencies:
 - Numpy
 - Kivy for graphics
 - HDF5 maybe for storage
 - Dask for parallel processing
 - pyFFTW maybe for faster FFT

# Concept
The basic building block object is a thing that has output ports, which behave kind of ndarrays
the basic object can be configured binding properties or whatever
once that is done, the output ports of the object present this interface:
* shape, (tuple of ints or None) represents the number of data points available in each axis, None means unbound = as many or as little as you ask
* dims, dict mapping name of each axis with a description of the axis, and the range of values available in the axis, as a slice (min,max,1/sampling_rate):
* dtype, returning the dtype of the values
* \__array__, to convert to numpy array, if possible = only if shape is a tuple of ints, returning the full range
* \__getitem__, indexable like a ndarray, with slices in all dimensions
    * indexes are in the unit defined by dims: the sampling rate is used to convert to int -- to be investigated
    * the returned object is either a ndarray or something that can be converted to a ndarray when needed (lazy elaboration of slices)