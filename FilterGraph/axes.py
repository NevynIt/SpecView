import class_definition_helpers as cdh
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
        return slice(self.start,self.stop,self.step)

class axis_info:
    unit = cdh.default("")
    annotations = cdh.default( () )
    axis_domain = cdh.default()
    index_domain = cdh.default()

    def to_index(self, x):
        raise NotImplementedError
    
    def from_index(self, indexes):
        raise NotImplementedError

class identity_axis(axis_info):
    @property
    def index_domain(self):
        return self.axis_domain

    def to_index(self, x):
        return x
    
    def from_index(self, indexes):
        return indexes