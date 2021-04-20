# Dependencies:
 - Numpy
 - Kivy for graphics
 - HDF5 maybe for storage
 - Dask maybe for parallel processing
 - pyFFTW maybe for faster FFT
# Concept
The basic building block object is a thing that has output ports, which behave kind of ndarrays
the basic object can be configured binding properties or whatever
once that is done, the output ports of the object present this interface:
* shape, (tuple of ints or None) represents the number of data points available in each axis, None means unbound = as many or as little as you ask
* dims, dict mapping name of each axis with a description of the axis, and the range of values available in the axis, as a slice (min,max,1/sampling_rate):
* dtype, returning the dtype of the values
* \_\_array__, to convert to numpy array, if possible = only if shape is a tuple of ints, returning the full range
* \_\_getitem__, indexable like a ndarray, with slices in all dimensions
    * indexes are in the unit defined by dims: the sampling rate is used to convert to int -- to be investigated
    * the returned object is either a ndarray or something that can be converted to a ndarray when needed (lazy elaboration of slices)

# more notes
```
ndfield
shape - tuple giving the lenght of each axis, which could be inf for unbounded axes
dims - tuple giving, per axis:
     bounds [min, max], which could be -inf or +inf for unbounded axes
     indexing, contiuous or discrete (= only integrals are allowed)
     callable that maps coord to index (with a param specifying, for discrete indexing, the rounding, which could be Floor, Ceil, Nearest=Round, or None - which also returns values between valid indexes)
          this has a inverse callable, which maps index to coord (
          both should throw if out of bounds
          useful properties to know could be: monotonic, linear, logarithmic, exponential, periodic

 dims - tuple of indexing functions
  the function goes from units to indexes
  unit name - could be seconds or Hz or piano note
  domain (where is the variable defined)
  range (what indexes are returned by the function, and are thus valid)
   domain and range can be defined as subsets of N, Z, R, C, and with bounds, conditions etc...
  properties
   sampled Y/N
    not all points in the domain can be returned by the field, the function accepts a parameter to specify the rounding approach (closest, floor, ceil, or None, which may return invalid indexes)
   serial Y/N (= left-total, see wiki)
    all points in the domain return indexes that exactly correspond to the coordinate requested
  inverse function, with the same attributes, but that translates from indexes to units
  
  
 2 functions:
     coord -> index
     index -> coord
 
ndfield
     shape (tuple of ints
     __getitem__
```

# more more notes