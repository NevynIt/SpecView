import class_definition_helpers as cdh
import numbers
import numpy as np
import warnings

EMPTY_SLICE = slice(None)

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
        ph = getattr(self, "_phase", None)
        if ph==None:
            if self.start == -np.inf:
                return 0
            else:
                return self.start % self.step
        else:
            return ph % self.step

    @phase.setter
    def phase(self, v):
        self._phase = v

    @property
    def sampling_rate(self):
        if self.step == None:
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
        if self.step == None:
            return np.inf #continuous domains have infinite samples
        return int((self.stop-self.start)/self.step)
    
    @property
    def countable(self) -> bool:
        n = self.nsamples
        return n != None and n < np.inf

    @property
    def lenght(self):
        return self.stop-self.start
    
    # def intersect(self, x):
    #     if isinstance(x,numbers.Number):
    #         if x >= self.start and x<=self.stop:
    #             return x
    #         else:
    #             return None
    #     elif isinstance(x, slice):
    #         if self.step == None:
    #             return slice(np.max(self.start,x.start),np.min(self.stop,x.stop),x.step)
    #         elif x.step == None:
    #             #adjust the start so that it lands on a valid coordinate iaw self.step
    #             raise NotImplementedError
    #         else:
    #             #TODO: more difficult, we have to consider the phase of the steps and how the steps will interact
    #             #rounding considerations apply. shall we only return if the coordinates are valid and exact?
    #             raise NotImplementedError

    def arange(self):
        if self.countable:
            ph = self.phase
            if ph == 0:
                return np.arange(self.start, self.stop, self.step, dtype=np.intp)
            else:
                return np.arange(self.start+self.step-self.phase, self.stop, self.step, dtype=np.intp)
        else:
            return None
    
    def slice(self):
        #makes no sense if it is not countable
        return slice(self.start,self.stop,self.step)

class base_axis_interpolator:
    props = cdh.property_store()
    def __init__(self, axis, pos):
        pass

    desired_indexes = props.observable()
    required_indexes = desired_indexes
    required_values = props.observable()
    desired_values = required_values

class axis_info:
    unit = cdh.default("")
    annotations = cdh.default( () )
    axis_domain = cdh.default()

    @property
    def index_domain(self):
        return self.axis_domain

    def to_index(self, x):
        return x
    
    def from_index(self, indexes):
        return indexes

    interpolator = cdh.default( base_axis_interpolator )

    def get_interpolator(self, pos):
        return self.interpolator(self, pos)

#define an alias
identity_axis = axis_info

class sampled_axis(axis_info):
    """
    axis_domain must be a constant or reactive property, returning a sampled or discrete and bounded domain
    index_domain and the transform functions are automatically generated
    """

    props = cdh.property_store()
    axis_domain = props.reactive( )
    interpolator = cdh.default( complex_axis_interpolator )
    interp_mode = cdh.default("floor")
    fill_mode = cdh.default("zeros")

    @props.cached(axis_domain)
    def index_domain(self):
        # assert self.axis_domain == None, "axis_domain is None"
        # assert self.axis_domain.nsamples == None or self.axis_domain.nsamples == np.inf, "axis_domain is not sampled nor discrete or not bounded"
        return domain(0, self.axis_domain.nsamples, 1)

    def __to_index_impl(self,coords):
        # assert self.axis_domain == None, "axis_domain is None"
        # assert self.axis_domain.step, "axis_domain is not sampled nor discrete"
        # assert self.axis_domain.start > -np.inf, "axis_domain is not bounded"
        return (coords - self.axis_domain.start)/self.axis_domain.step

    def to_index(self, x):
        if isinstance(x, slice):
            x1 = slice(x.start or self.axis_domain.start, x.stop or self.axis_domain.stop, x.step or self.axis_domain.step)
            return slice(self.__to_index_impl(x1.start), self.__to_index_impl(x1.stop), x1.step/self.axis_domain.step)
        else:
            #this works for scalars or ndarrays of indexes
            return self.__to_index_impl(x)

    def __from_index_impl(self,indexes):
        return self.axis_domain.start + (indexes*self.axis_domain.step)

    def from_index(self, indexes):
        if isinstance(indexes, slice):
            i1 = slice(indexes.start or self.index_domain.start, indexes.stop or self.index_domain.stop, indexes.step or self.index_domain.step)
            return slice(self.__from_index_impl(i1.start), self.__from_index_impl(i1.stop), i1.step*self.axis_domain.step)
        else:
            return self.__from_index_impl(indexes)