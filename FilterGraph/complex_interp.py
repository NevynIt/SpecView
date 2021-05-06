from .axes import *
import scipy.interpolate

#TODO: detect and optimise for obvious cases

class complex_axis_interpolator(base_axis_interpolator):
    props = cdh.property_store()
    
    def __init__(self, axis, pos, interp_mode = None, fill_mode = None):
        self.axis = axis
        self.pos = pos
        if axis.index_domain.step != 1:
            raise NotImplementedError

        if interp_mode:
            self.interp_mode = interp_mode
        elif hasattr(axis, "interp_mode"):
            self.interp_mode = axis.interp_mode

        if fill_mode:
            self.fill_mode = fill_mode
        elif hasattr(axis, "fill_mode"):
            self.fill_mode = axis.fill_mode
        
    desired_indexes = props.reactive()

    def to_index_array(self, indexes):
        if isinstance(indexes, numbers.Number):
            return indexes
        if isinstance(indexes, slice):
            domain = self.axis.index_domain
            step = indexes.step or 1
            if step == 0 or step == None:
                raise IndexError
            if step > 0:
                start = indexes.start or domain.start
                stop = indexes.stop or domain.stop
            elif step < 0:
                warnings.warn("maybe incorrect, boundaries might be wrong")
                start = indexes.start or (domain.stop - domain.step)
                stop = indexes.stop or (domain.start - domain.step)
            return np.arange(start,stop,step)

    interp_mode = props.reactive( "floor" )
    #possible values are those in interp_order, plus floor, ceil, round or throw

    interp_order = {
                "nearest": 1,
                "nearest-up": 1,
                "zero": 2,
                "linear":1,
                "quadratic":2,
                "cubic":3,
                "previous":1,
                "next":1,
                0:1,
                1:1,
                2:2,
                3:3,
                4:4
            }

    @props.cached(desired_indexes, interp_mode)
    def interpolation_indexes(self):
        "return indexes that are aligned with the phase and step of axis.index_domain - limited to whole numbers for now"
        di = self.to_index_array(self.desired_indexes)
        im = self.interp_mode
        if im == "floor":
            return np.floor(di).astype(np.int_)
        elif im == "ceil":
            return np.ceil(di).astype(np.int_)
        elif im == "round":
            return np.round(di).astype(np.int_)
        elif im == "throw":
            if ((di % 1) != 0).any():
                raise IndexError
            return np.astype(np.int_)
        elif im in complex_axis_interpolator.interp_order:
            selector = (di % 1) == 0
            constantset = di[selector]
            interpset = di[~selector]            
            af = np.floor(interpset)
            ac = np.ceil(interpset)            
            tmp = []
            for j in range(complex_axis_interpolator.interp_order[im]):
                tmp.append(af - j)
                tmp.append(ac + j)
            interpset = np.concatenate(tmp)
            return np.union1d(constantset, interpset).astype(np.int_)
        else:
            raise NotImplementedError
     
    fill_mode = props.reactive( "zeros" )
    #possible values are zeros, reflect, nearest, repeat

    @props.cached(interpolation_indexes, fill_mode)
    def bounded_indexes(self):
        "return indexes that are aligned with the boundaries of axis.index_domain - limited to whole numbers for now"
        ii = self.interpolation_indexes
        fm = self.fill_mode
        domain = self.axis.index_domain    
        if fm == "zeros":
            self.selector = (ii >= domain.start) & (ii < domain.stop)
            selected = ii[self.selector]
        elif fm == "reflect":
            selected = ii.copy()
            swapped = True
            while swapped:
                swapped = False
                below = selected < domain.start
                if below.any():
                    selected -= domain.start
                    selected[below] = - selected[below]
                    selected += domain.start
                    swapped = True
                above = selected >= domain.stop
                if above.any():
                    selected -= domain.stop
                    selected[above] = - selected[above]
                    selected += domain.stop
        elif fm == "nearest":
            selected = np.clip(ii,domain.start,domain.stop-domain.step)
        elif fm == "repeat":
            selected = (domain.start + ((ii-domain.start) % (domain.stop-domain.start))).astype(np.int_)
        else:
            raise NotImplementedError
        res, self.inverse = np.unique(selected, return_inverse=True)
        return res

    #alias
    required_indexes = bounded_indexes
        
    required_values = props.reactive()
   
    @props.cached(required_values, fill_mode, bounded_indexes, interpolation_indexes)
    def unbounded_values(self):
        "return values for all the interpolation_indexes"
        #use the reconstruction array to get the unbounded values
        res = self.required_values
        if len(res) > 0:
            res = np.take(res, self.inverse, self.pos)
        if self.fill_mode == "zeros":
            tmpshape = list(self.required_values.shape)
            tmpshape[self.pos] = len(self.interpolation_indexes) #FIXME: does not work with scalars
            tmp = np.zeros(tmpshape, self.required_values.dtype)
            tmp[self.selector] = res
            res = tmp
        return res

    @props.cached(unbounded_values, interp_mode, interpolation_indexes, desired_indexes)
    def interpolated_values(self):
        "return values for all the desired_indexes"
        #use the unbounded values to reconstruct the interpolated values
        im = self.interp_mode
        uv = self.unbounded_values
        if im in ("floor", "ceil", "round"):
            return uv
        elif im in complex_axis_interpolator.interp_order:
            di = self.to_index_array(self.desired_indexes)
            ii = self.interpolation_indexes
            f = scipy.interpolate.interp1d(ii,uv,axis=self.pos,kind=im)
            return f(di)
        else:
            raise NotImplementedError

    #alias
    desired_values = interpolated_values

class complex_field_interpolator:
    props = cdh.property_store()
    
    axes_interp = props.reactive()

    def __init__(self, axes):
        self.axes_interp = [a.get_interpolator(i) for i, a in enumerate(axes)]

    def interpolate(self, space, indexes):
        self.desired_indexes = indexes
        self.required_values = space[self.required_indexes]
        return self.desired_values

    desired_indexes = props.reactive()

    @props.cached(desired_indexes, axes_interp)
    def required_indexes(self):
        "collect the required indexes from each axis in order (which also prepares the interpolators)"
        res = []
        for ai,di in zip(self.axes_interp, self.desired_indexes):
            ai.desired_indexes = di
            res.append(ai.required_indexes)
        return tuple(res)
        
    required_values = props.reactive()
   
    @props.cached(required_values, axes_interp, required_indexes)
    def desired_values(self):
        "ask each axis in order to perform the interpolation"
        rv = self.required_values
        for i, ai in enumerate(self.axes_interp):
            ai.required_values = rv
            rv = ai.desired_values
        return rv
