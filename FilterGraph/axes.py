import class_definition_helpers as cdh
import numbers
import numpy as np

class domain:
    """ start is a valid coordinate, and determines the phase for the sampling """

    @cdh.assignargs(start=-np.inf, stop=np.inf, step = None, phase = None)
    def __init__(self, start, stop, step, phase):
        pass

    @property
    def step(self):
        return getattr(self, "_step", None)
    @step.setter
    def step(self, v):
        if v == 0 or v==np.inf or v==-np.inf:
            v = None
        self._step = v

    @property
    def phase(self):
        if self.step == None:
            return None
        ph = getattr(self, "_step", None)
        if ph==None:
            if self.start == -np.inf:
                return 0
            else:
                return self.start % self.step
        else:
            return ph % self.step
    @phase.setter
    def phase(self, v)
        self._phase = v

    @property
    def sampling_rate(self):
        if step == None:
            return None
        return 1/self.step
    @sampling_rate.setter
    def sampling_rate(self, v):
        if v == 0 or v == None:
            self.step = None
        else:
            self.step = 1/v
        
    @property
    def nsamples(self):
        if step == None:
            return None
        return (self.stop-self.start)/self.step
    
    @property
    def lenght(self):
        return self.stop-self.start
    
    def intersect(self, x):
        if isinstance(x,numbers.Number):
            if x >= self.start and x<=self.stop:
                return x
            else:
                return None
        elif isinstance(x, slice):
            if self.step == None:
                return slice(np.max(self.start,x.start),np.min(self.stop,x.stop),x.step)
            elif x.step == None:
                #adjust the start so that it lands on a valid coordinate iaw self.step
                raise NotImplementedError
            else:
                #TODO: more difficult, we have to consider the phase of the steps and how the steps will interact
                #rounding considerations apply. shall we only return if the coordinates are valid and exact?
                raise NotImplementedError

    def arange(self):
        l = self.lenght
        if l>0 and l<np.inf and self.step != None:
            ph = self.phase
            if ph == 0:
                return np.arange(self.start, self.stop, self.step)
            else:
                return np.arange(self.start+self.step-self.phase, self.stop, self.step)
        else:
            return None

class axis_info:
    unit = cdh.default("")
    annotations = cdh.default( () )
    axis_domain = cdh.default( None )
    index_domain = cdh.default( None )
    def to_index(self, x):
        raise NotImplementedError
    def from_index(self, i):
        raise NotImplementedError
    interpolator = cdh.parent_reference_host( cdh.default( interpolator_base() ) ) #TODO: TEST TEST

class identity_axis(axis_info):
    @property
    def index_domain(self):
        return self.axis_domain
    
    def to_index(self,x):
        return x
    def from_index(self,i):
        return i

class interpolator_base:
    def find_indexes(self, i):
        "find the indexes required to provide the interpolated value for the indexes in i"
        return i
    
    def interpolate(self, i, ip, vp, axis=None):
        """
        vp is n-dimensional, but interpolate needs only to consider the given axis, and return a new n-dim array
        in which based on the values for the coordinates ip (chosen by find_indexes) the values in the coordinates i
        are returned.
        e.g. a 3d array with linear interpolation requires 8 data points per interpolated point, 2 per axis
             if we are to linearly interpolate, we get first 4 data points interpolated along 1 axis,
             then 2 data points interpolated along 2 axis, then 1 data point interpolated along all 3

        When axis = None, i is multidimensional and works on the whole ndarray
        """
        return vp

class floor_interpolator(interpolator_base):
    def find_indexes(self, i):
        return np.floor(i)
    
    def interpolate(self, i, ip, vp, axis):
        return vp

class linear_sampled_axis(axis_info):
    """
    axis_domain must be a constant or reactive property, returning a sampled or discrete and bounded domain
    index_domain and the transform functions are automatically generated
    """

    props = cdh.property_store()
    axis_domain = props.reactive( None )
    interpolator = cdh.parent_reference_host( cdh.default( floor_interpolator() ) ) #TODO: TEST TEST

    @props.cached(axis_domain)
    def index_domain(self):
        # assert self.axis_domain == None, "axis_domain is None"
        # assert self.axis_domain.nsamples == None or self.axis_domain.nsamples == np.inf, "axis_domain is not sampled nor discrete or not bounded"
        return domain(0, self.axis_domain.nsamples, 1)

    def __to_index_impl(self,x):
        # assert self.axis_domain == None, "axis_domain is None"
        # assert self.axis_domain.step, "axis_domain is not sampled nor discrete"
        # assert self.axis_domain.start > -np.inf, "axis_domain is not bounded"
        return (x - self.axis_domain.start)/self.axis_domain.step

    def to_index(self, x):
        if isinstance(x, slice):
            x1 = slice(x.start or self.axis_domain.start, x.stop or self.axis_domain.stop, x.step or self.axis_domain.step)
            return slice(self.__to_index_impl(x1.start), self.__to_index_impl(x1.stop), x1.step/self.axis_domain.step)
        else:
            #this works for scalars or ndarrays of indexes
            return self.__to_index_impl(x)

    def __from_index_impl(self,i):
        return self.axis_domain.start + (i*self.axis_domain.step)

    def from_index(self, i):
        if isinstance(x, slice):
            i1 = slice(x.start or self.index_domain.start, x.stop or self.index_domain.stop, x.step or self.index_domain.step)
            return slice(self.__from_index_impl(i1.start), self.__from_index_impl(i1.stop), i1.step*self.axis_domain.step)
        else:
            return self.__from_index_impl(i)
