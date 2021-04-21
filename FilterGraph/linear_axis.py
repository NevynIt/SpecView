import class_definition_helpers as cdh #class definition helpers
from .ndfield import *
import numpy as np

class linear_sampled_axis(axis_info):
    props = cdh.property_store()
    unit = props.constant(None)
    @property
    def params(self):
        "return (start, stop, step)"
        return (0,0,1)

    @cdh.autocreate
    class axis_domain:
        parent = cdh.autocreate.parent_reference()
        @property
        def stop(self):
            return self.parent.params[0]
        @property
        def stop(self):
            return self.parent.params[1]
        @property
        def step(self):
            return self.parent.params[2]
        discrete = cdh.property_store.constant(False)
    
    @cdh.autocreate
    class index_domain:
        parent = cdh.autocreate.parent_reference()
        start = cdh.property_store.constant(0)
        @property
        def stop(self):
            return (self.parent.params[1]-self.parent.params[0])/self.parent.params[2]
        step = cdh.property_store.constant(1)
        discrete = cdh.property_store.constant(True)

    def to_index(self, x, rounding=None):
        #assume x is either a number - things change for ndarrays
        if x<self.params[0] or x>=self.params[1]:
            raise IndexError("out of bounds")

        tmp = (x-self.params[0])/self.params[2]

        #the logic below should be moved to axis_info
        if rounding == None:
            rounding = self.rounding
        if rounding == "floor":
            tmp = np.floor(tmp)
        elif rounding == "ceil":
            tmp =  np.ceil(tmp)
        elif rounding == "round":
            tmp =  np.round(tmp)
        elif rounding == "throw":
            if tmp-np.int_(tmp) != 0: #this will raise for numpy arrays?
                raise IndexError("Inexact index")
            else:
                pass
        elif rounding == "exact":
            pass
        
        return tmp

    def from_index(self, i, rounding=None):
        if i<0 or i>=self.params[1]/self.params[2]:
            raise IndexError("out of bounds")

        #assume i is either a number or a numpy array
        if rounding == None:
            rounding = self.rounding
        #the logic below should be moved to axis_info
        if rounding == "floor":
            i = np.floor(i)
        elif rounding == "ceil":
            i =  np.ceil(i)
        elif rounding == "round":
            i =  np.round(i)
        elif rounding == "throw" or rounding == "exact":
            if (i-np.int_(i) != 0).any():
                raise IndexError("Inexact index")

        return i*self.params[2] + self.params[0]

    annotations = props.constant( tuple() )

    mapped = props.reactive(False)
    rounding = props.reactive("floor")

    def __getitem__(self, key):
        return self.to_index(key)

class linear_discrete_axis(axis_info):
    pass

class identity_axis(axis_info):
    pass