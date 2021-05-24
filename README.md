# Rework of axes May 23
Delete domain class, unify in axis_info.
Axis info is the one containing directly:
 - the boundaries of the axis, in coordspace
 - the origin of indexes (i.e. the coord of index 0)
 - the scale of indexes (i.e. the coord if index 1 minus the coord of index 0)

# Concept again May 16
Simplest form of ndarray is a class:
- indexable
- with a dtype
- with axes to describe the axes
- with shape to describe the number of samples available in each axis (calculated)


# Concept again
The basic idea is that I am designing objects that refer to n-dimensional fields

There will be objects that represent the field, and that map from coordinates in n axes
to something (scalars, vectors, objects, as in ndarrays)
these axes can be bounded, unbounded, continuous, sampled or discrete
objects can provide new fields that are based on parameters (including other fields)
examples are objects that sample a continuous axis, or that make a bounded one unbounded (e.g. making it periodic).
When new fields are based on other fields, these should be, as much as possible, lazy views over the others. when a field is a projection of another field (including the field resulting from a sampler or an interpolator), and regardless if this other field is actually accessible as an object, it is useful to have a function that maps coordinates in the new field to coordinates in the old, and vice-versa

# Field object interface:
Attributes:
- `shape`: `tuple` of numbers with the lengh of each axis. can be `np.inf`, `-np.inf` or `None` if undefined
- `axes`: axes_object
- `coordspace`: array interface over the original domain
- `samplespace`: array interface over the sampled domain - alias of coordspace if not sampled
- `dtype`: the data type returned as values

Methods:
- `to_index(coords)`
  - takes coordinates or ranges in the original domain and returns indexes or slices in the domain of the sampled field
- `from_index(coords)`
  - takes coordinates or slices in the domain of the sampled field and returns coordinates or ranges in the original domain
- `__getitem__`: alias for access to `samplespace`
- `__array__`: if the field is discrete or sampled and bounded on all axes, it provides returns a `numpy.ndarray`

# axes_object interface:
Can be seen as a list of axes, indexable by position. In reality it is likely to be an autocreate object derived from axes_object, which has the following structure:

Attributes:
- axes: class attribute, which subclasses should set to a tuple of the actual axes declared (as autocreate) in the axes_object
- parent: reference to parent class

```
import ndfields as ndf

class myfield(ndf.ndfield):
     @autocreate
     class axes(ndf.axes_object):
          @autocreate
          class time(ndf.linear_sampled_axis):
               ...set the parameters
          
          @autocreate
          class channels(ndf.linear_discrete_axis):
               ...set the parameters
          
          axes = (time, channels)
```

# Interesting fields:
## Sound
Dimensions:
- `time`: continuous, measured in seconds
- `channels`: discrete

Values: Real number, representing the pressure on each microphone

# Field transformations
## Caching
Parameters:
- original field (must be sampled or discrete along all axes)
- page-size: tuple with page size per axis (a page is a hyper-parallelogram with the defined dimensions)

Dimensions:
- same as the original field

Values:
- same as the original field

Attributes:
- `pagesize`: bytes used by each page
- `oldestpage`: timestamp of the page used least recently
- `loadedpages`: number of pages currently loaded

Methods:
- `unloadpage`: unloads the least recently used page from memory
- `invalidate(range)`: invalidates (and unloads) all the pages that intersect the given range (expressed as in `__getattr__`)

## Sampling
Parameters:
- original field
- sampling space: tuple of (phase, rate) or None for axes that are not sampled
- rounding: approach to use when indexes are not exact in to_index or from_index

Dimensions: 
- same as the original field for some (continuous, discrete or whatever)
- discrete, indexed by sample, for one or more fields

Values: same as the original field

## Quantisation (maybe)
Parameters:
- original field
- quantization parameters: phase, step
- rounding

Dimensions:
- same as the original field

Values:
- quantised version of the original values

## Bounding
Parameters:
- original field
- `range`: tuple of (start, stop) or None for axes that are not to be bound
- `clip`: (min, max) or None to clip the values

Dimensions:
- same as the original field, but with some applicable to a limited space

Values:
- same as the original field, for a subset of the coordinates

## Padding:
Parameters:
- original field
- padding value: what to return outside the original bounds, can be a number or a function defined over the same n-dimensional space or a field
- axes: which axes to pad, and in which direction (towards -inf, or +inf, or both)

Dimensions:
- same as the original field, with some unbounded

Values:
- same as the original field, or the padding value where the original field was not defined

## Linear transform
It assumes that ([value or coordinate]*scale + offset) will return something valid

Parameters:
- original field
- transformations of coordinates: tuple of (offset and scale) or None for axed not transformed
- transformation of values: offset and scale or None for axes not transformed

Methods:
- to_value()
- from_value()

## FFT
Calculates the FFT of the original field over the given axis. The number of elements in the window field provided determines the number of samples that the FFT will use (and therefore the amount of original field space that will be considered as the periodic subset in each point). Window-lenght samples are taken from the original field starting from the position requested over the axis minus window-lenght/2.

Parameters:
- `axis` to transform (axis 0 by default)
- original field (must be sampled and have numeric values)
- `window`: a 1-dimensional discrete field returning the window function used on the samples

Dimensions:
- same as the original with the following addition
- the last dimension is the frequency bins, it's discrete and contains as many items as the size of the window, the axis domain is frequencies up to the Nyquist frequency, given by 1/sample-rate / 2

Values:
- Complex numbers as returned by FFT

Methods:
- `set_window(lenght, fnc or name or None)`:
  - length is defined in the unit of the axis in the original field
  - name can be:
     - one of "hanning", "blackman", etc... to use one of the default numpy windowing functions
     - a callable, which will receive a single float from 0 to 1, and should return a float between 0 and 1
     - None is equivalent to using a single windowing function that always returns 1

## Phase vocoder
Start from [audiotsm](https://github.com/Muges/audiotsm/) analysis_synthesis for the implementation, and leverage the FFT field for computation

Parameters:
- original field (must be a FFT field over something else)
- scale factor: float, 1 = unscaled
- analysis hop
- equalization: optional field that gives the amplification to apply per sample per frequency bin; it must have the same dimensions and shape as the FFT field

Dimensions:
- same as the original field of the input FFT field

Values:
- same domain as the original field of the input FFT field 

## Interpolation
Parameters:
- original field
- method: nearest neighbour, linear, polynomial

## Logarithmic view
Parameters:
- original field
- axis to provide a logaritmic view of
- method: interpolation, integral (useful for frequency bins)

## numpy.ufunc application (maybe?)
returns a field that applies the result of the given ufunc over the provided source fields when indexed. all fields are indexed with the same indexes, and the result is passed to the ufunc. This field could be used to implement operations between fields and/or ndarrays using the numpy universal functions

Parameters:
- original fields: must all be sampled or discrete and bounded, and broadcastable to the same shape
- ufunc, method: same as in `__array_ufunc__`

Dimensions:
- discrete "thing" based on whatever comes from the ufunc (?)

Values:
- whatever comes from the

---
---
previous ideas...
---
---
---
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