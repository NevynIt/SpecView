from .axes import *
import scipy.interpolate

#TODO: detect and optimise for obvious cases, and support slices directly

def to_index_array(indexes, axis):
    if isinstance(indexes, np.ndarray):
        return indexes
    elif isinstance(indexes, numbers.Number):
        return indexes
    elif isinstance(indexes, slice):
        domain = axis.index_domain
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

class axis_interpolator(base_axis_sampler):
    def __init__(self, axis, pos, interp_mode = None):
        self.axis = axis
        self.pos = pos
        if axis.index_domain.step != 1:
            raise NotImplementedError
        if interp_mode:
            self.interp_mode = interp_mode
        elif hasattr(axis, "interp_mode"):
            self.interp_mode = axis.interp_mode

    interp_mode = cdh.default( "floor" )
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
 
    def identify_indexes(self, di):
        "return indexes that are aligned with the phase and step of axis.index_domain - limited to whole numbers for now"
        di = to_index_array(di, self.axis)
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
        elif im in axis_interpolator.interp_order:
            selector = (di % 1) == 0
            constantset = di[selector]
            interpset = di[~selector]            
            af = np.floor(interpset)
            ac = np.ceil(interpset)            
            tmp = []
            for j in range(axis_interpolator.interp_order[im]):
                tmp.append(af - j)
                tmp.append(ac + j)
            interpset = np.concatenate(tmp)
            self.desired_indexes = di
            self.interpolation_indexes = np.union1d(constantset, interpset).astype(np.int_)
            return self.interpolation_indexes
        else:
            raise NotImplementedError

    def calculate_values(self, rv):
        "return values for all the desired_indexes"
        #use the unbounded values to reconstruct the interpolated values
        im = self.interp_mode
        if im in ("floor", "ceil", "round", "throw"):
            return rv
        elif im in axis_interpolator.interp_order:
            f = scipy.interpolate.interp1d(self.interpolation_indexes,rv,axis=self.pos,kind=im)
            return f(self.desired_indexes)
        else:
            raise NotImplementedError

class axis_extender(base_axis_sampler):
    def __init__(self, axis, pos, fill_mode = None):
        self.axis = axis
        self.pos = pos

        if fill_mode:
            self.fill_mode = fill_mode
        elif hasattr(axis, "fill_mode"):
            self.fill_mode = axis.fill_mode    

    fill_mode = cdh.default( "zeros" )
    #possible values are zeros, reflect, nearest, repeat

    def identify_indexes(self, di):
        "return indexes that are aligned with the boundaries of axis.index_domain - limited to whole numbers for now"
        di = to_index_array(di, self.axis)
        fm = self.fill_mode
        domain = self.axis.index_domain    
        self.inverse = None

        if fm == "throw":
            if ((di < domain.start) | (di >= domain.stop)).any():
                raise IndexError
            return di
        elif fm == "zeros":
            self.desired_indexes = di
            self.selector = (di >= domain.start) & (di < domain.stop)
            selected = di[self.selector]
        elif fm == "reflect":
            selected = di.copy()
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
            selected = np.clip(di,domain.start,domain.stop-domain.step)
        elif fm == "repeat":
            selected = (domain.start + ((di-domain.start) % (domain.stop-domain.start))).astype(np.int_)
        else:
            raise NotImplementedError
        res, self.inverse = np.unique(selected, return_inverse=True)
        return res

    def calculate_values(self, rv):
        "return values for all the desired_indexes"
        #use the reconstruction array to get the unbounded values
        res = rv
        if self.inverse is None:
            return res

        if len(res) > 0:
            res = np.take(res, self.inverse, self.pos)
        if self.fill_mode == "zeros":
            tmpshape = list(rv.shape)
            tmpshape[self.pos] = len(self.desired_indexes)
            tmp = np.zeros(tmpshape, rv.dtype)
            tmp[self.selector] = res
            res = tmp
        return res