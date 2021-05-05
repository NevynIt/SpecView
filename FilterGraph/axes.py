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

class axis_interpolator:
    props = cdh.property_store()
    
    def __init__(self, axis):
        self.axis = axis
        
    desired_indexes = props.reactive()

    interp_mode = props.reactive( "floor" )
    @props.cached(desired_indexes, interp_mode)
    def interpolation_indexes(self):
        "return indexes that are aligned with the phase and step of axis.index_domain"
        #transform anything to a ndarray of indexes first
        raise NotImplementedError
     
    fill_mode = props.reactive( "zeros" )
    @props.cached(interpolation_indexes, fill_mode)
    def bounded_indexes(self):
        #transform anything to a ndarray of indexes first
        #trasform each index individually
        #use np.unique(inverse = True) to get unique and sorted points, store the reconstruction array
        "return indexes that are aligned with the boundaries of axis.index_domain"
        raise NotImplementedError

    #alias
    required_indexes = bounded_indexes
        
    required_values = props.reactive()
   
    @props.cached(required_values, fill_mode, bounded_indexes, interpolation_indexes)
    def unbounded_values(self):
        "return values for all the interpolation_indexes"
        #use the reconstruction array to get the unbounded values
        raise NotImplementedError

    @props.cached(unbounded_values, interp_mode, interpolation_indexes, desired_indexes)
    def interpolated_values(self):
        "return values for all the desired_indexes"
        #use the unbounded values to reconstruct the interpolated values
        raise NotImplementedError
   
    #alias
    desired_values = interpolated_values

class axis_info:
    unit = cdh.default("")
    annotations = cdh.default( () )
    axis_domain = cdh.default()
    index_domain = cdh.default()
    pos = cdh.default() #position within the field axes array

    @property
    def interpolator(self):
        "get a thread specific interpolator object"
        return axis_interpolator(self)

#define an alias
identity_axis = axis_info

class sampled_axis(axis_info):
    """
    axis_domain must be a constant or reactive property, returning a sampled or discrete and bounded domain
    index_domain and the transform functions are automatically generated
    """

    props = cdh.property_store()
    axis_domain = props.reactive( domain(0,0,1) )


    #TODO: replace using axis_interpolator
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

    #filler options are: "zeros", "nearest", "reflect", "mirror", "wrap", or a specific value
    fill_mode = cdh.default("zeros")

    #--comments here taken when the idea was to do this in ndarray
    #split ip in areas within the sample space and areas outside, axis per axis
    #-> ind is a tuple with len equal to len(axes)
    #   create 3 indexes per element of ind (things < start, things in between, things > stop)
    #      single scalar indexes are easy, the scalar goes in one of the bins and the others are empty
    #      slices are slightly more complicated, one slice could become up to three slices
    #      ndarrays should be first sorted, then split with the same logic as the simple scalar

    # 3d example: [[None,sliceA,None],[sliceB1,sliceB2,None],[ndarrayC1, ndarrayC2, ndarrayC3]]
    # this becomes conceptally a 3d array with shape (3,3,3), but some dimensions can be reduced and
    # this becomes a 3d array with shape (1,2,3) and contents:
    # [ [ (sliceA,sliceB1,ndarrayC1),(sliceA,sliceB1,ndarrayC2),(sliceA,sliceB1,ndarrayC3) ],
    #   [ (sliceA,sliceB2,ndarrayC1),(sliceA,sliceB2,ndarrayC2),(sliceA,sliceB2,ndarrayC3) ] ]

    #iterate all the combinations equivalent to the subspaces that are inside/outside one or more axes
    #call samplespace for the single one inside, if any. (sliceA,sliceB2,ndarrayC2) in the example above
    #call outerspace for the ones outside (all the others)
    # vp = self.samplespace(indexes)
    #recombine the pieces into a single ndarray (using numpy.blocks), based on how things had been cut
    #      single scalar indexes are easy, the bit with the scalar is the only thing used
    #      slices are slightly more complicated, as up to three pieces could be collated
    #      ndarrays should be first collated and then reshuffled
    #reshuffle the ndarray axes to come back to the order requested initially

    # def expand_indexes(self, indexes, constrain_bounds = True):
    #     indexes = self.expand_ellipsis(indexes)
    #     domains = [a.index_domain for a in self.axes]
    #     ind = []
    #     for i in range(len(indexes)):
    #         k = indexes[i]
    #         if isinstance(k, slice):
    #             domain_slice = domains[i].slice()
    #             if k == EMPTY_SLICE or k == domain_slice:
    #                 ind.append(domain_slice)
    #             else:
    #                 step = k.step or domain_slice.step
    #                 if step == 0 or step == None:
    #                     raise IndexError
    #                 if step <0:
    #                     warnings.warn("maybe incorrect, boundaries might be wrong")
    #                     start = k.start or (domain_slice.stop - domain_slice.step)
    #                     stop = k.stop or (domain_slice.start - domain_slice.step)
    #                     if constrain_bounds:
    #                         start = min(start, domain_slice.stop - domain_slice.step)
    #                         stop = max(stop, domain_slice.start - domain_slice.step)
    #                 else:
    #                     start = k.start or domain_slice.start
    #                     stop = k.stop or domain_slice.stop
    #                     if constrain_bounds:
    #                         start = max(start, domain_slice.start)
    #                         stop = min(stop, domain_slice.stop)
    #                 n = max(0,(stop-start)/step)
    #                 if n == np.inf:
    #                     raise IndexError
    #                 ind.append(slice(start,stop,step))
    #         elif isinstance(k, numbers.Number):
    #                 ind.append(k)
    #         else:
    #             k = np.asanyarray(k)
    #             if issubclass(k.dtype.type, numbers.Integral):
    #                 ind.append(k)
    #             elif k.dtype == np.bool_:
    #                 raise NotImplementedError
    #             else:
    #                 raise IndexError
    #     return tuple(ind)

    def to_samples(self, indexes):
        #indexes can be: number, slice, iterable of bool, iterable of numbers -- or -- iterable of (slices or iterables of numbers)
        #the return value is an equivalent but easier to manage indexes parameter, and a tuple containing: integers, slices or ndarrays of integers
        #each element in the tuple represents a subset of the sampling space that needs to be sampled
        #TODO: limit the samples requested in the boundaries of index_domain, using the fill_mode

        if isinstance(indexes, numbers.Number):
            samples = (int(np.floor(indexes)),)
        else:
            if isinstance(indexes, slice):
                indexes = (indexes, )
            
            indexes = np.asanyarray(indexes)

            t = type(indexes[0])
            if issubclass(t, np.bool_):
                if len(indexes) != self.index_domain.nsamples:
                    raise IndexError
                return (np.arange(len(indexes))[indexes],)

            if issubclass(t, numbers.Number):
                #works both for iterables of numbers and 2d iterables
                if len(t.shape) > 2:
                    raise IndexError
                return np.floor(indexes).astype(np.int_)

            if issubclass(t, slice):
                samples = ()
                for s in indexes:
                    step = s.step or 1
                    if step > 0:
                        start = s.start or 0
                        stop = s.stop or self.axis_domain.nsamples
                        if step % 1 == 0:
                            res += slice(int(np.floor(start)), int(np.floor(stop)), int(step))
                        else:
                            #there may be a better way... maybe using arange
                            res += slice(int(np.floor(start)), int(np.ceil(stop)), 1)
                    elif step < 0:
                        warnings.warn("step < 0 not fully designed")
                        start = s.start or self.axis_domain.nsamples-1
                        stop = s.start or -1
                        if step % 1 == 0:
                            res += slice(int(np.floor(stop)), int(np.floor(start)), int(-step))
                        else:
                            #there may be a better way... maybe using arange
                            res += slice(int(np.floor(stop)), int(np.ceil(start)), 1)
                    else:
                        raise IndexError
            else:
                raise IndexError
        return (index, samples)
    
    def interpolate(self, indexes, ip, vp, axis):
        if isinstance(indexes, numbers.Number):
            return vp

        if isinstance(indexes, slice):
            indexes = (indexes, )

        indexes = np.asanyarray(indexes)

        t = type(indexes[0])
        if issubclass(t, np.bool_):
            return vp

        if issubclass(t, numbers.Number):
            if len(indexes.shape) > 1:
                #recombine the sets
                raise NotImplementedError
            return vp

        if isinstance(indexes, slice):
            if indexes.step > 0:
                if indexes.step % 1 == 0:
                    return vp
                else:
                    key = [EMPTY_SLICE, ] * len(vp.shape)
                    key[axis] = np.floor(np.arange(0,indexes.stop-indexes.start,indexes.step)).astype(np.int_)
                    return vp[tuple(key)]
            elif indexes.step < 0:
                if indexes.step % 1 == 0:
                    vp.flip(axis)
                    return vp
                else:
                    key = [EMPTY_SLICE, ] * len(vp.shape)
                    key[axis] = np.flip(np.floor(np.arange(0,indexes.start-indexes.stop,-indexes.step))).astype(np.int_)
                    return vp[tuple(key)]
        else:
            return vp