from .axes import *
import scipy.interpolate

class interpolated_axis(sampled_axis):
    "uses scipy.interpolate.interp1d, assumes a discrete field with index_domain starting with step 1 and phase 0"
    
    kind = cdh.default("linear")
    
    order = {
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

    def to_samples(self, indexes):
        #TODO: avoid interpolation if not required
        if isinstance(indexes, numbers.Number):
            a = np.array( (indexes,) )
        elif isinstance(indexes, np.ndarray):
            a = indexes
        elif isinstance(indexes, slice):
            a = np.arange(indexes.start,indexes.stop,indexes.step)
        else:
            raise NotImplementedError
        selector = (a % 1) == 0
        constantset = a[selector]
        interpset = a[~selector]

        af = np.floor(interpset)
        ac = np.ceil(interpset)
        tmp = []
        for j in range(scipy_interpolator.order[self.kind]):
            tmp.append(af - j)
            tmp.append(ac + j)
        interpset = np.concatenate(tmp)
        return np.union1d(constantset, interpset).astype(np.int_)

    def interpolate(self, indexes, ip, vp, axis):
        if isinstance(indexes, numbers.Number):
            a = np.array( (indexes,) )
        elif isinstance(indexes, np.ndarray):
            a = indexes
        elif isinstance(indexes, slice):
            a = np.arange(indexes.start,indexes.stop,indexes.step)
        else:
            raise NotImplementedError
        f = scipy.interpolate.interp1d(ip,vp,axis=axis,kind=self.kind)
        return f(a)