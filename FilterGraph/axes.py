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

class base_axis_sampler:
    def __init__(self, axis, pos):
        pass

    def identify_indexes(self, di):
        return di

    def calculate_values(self, rv):
        return rv

class combined_axis_sampler(base_axis_sampler):
    def __init__(self, samplers, axis, pos):
        self.chain = tuple([s(axis,pos) for s in samplers])
    
    def identify_indexes(self, di):
        for s in self.chain:
            di = s.identify_indexes(di)
        return di
    
    def calculate_values(self, rv):
        for s in reversed(self.chain):
            rv = s.calculate_values(rv)
        return rv

class axis_info:
    unit = cdh.default("")
    annotations = cdh.default( () )
    axis_domain = cdh.default()
    interp_mode = cdh.default( "throw" )
    fill_mode = cdh.default( "throw" )
    page_size = cdh.default( None )

    @property
    def index_domain(self):
        return self.axis_domain

    def to_index(self, x):
        return x
    
    def from_index(self, indexes):
        return indexes

    sampler = cdh.default( None )

    def get_sampler(self, pos):
        if self.sampler == None:
            return base_axis_sampler(self, pos)
        elif isinstance(self.sampler, type) and issubclass(self.sampler, base_axis_sampler):
            return self.sampler(self, pos)
        elif isinstance(self.sampler, (tuple, list)):
            return combined_axis_sampler(self.sampler, self, pos)

#define an alias
identity_axis = axis_info