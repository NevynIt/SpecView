from .axes import *
import scipy.interpolate

class scipy_interpolator(interpolator_base):
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

    def find_indexes(self, i):
        if isinstance(i, numbers.Number):
            a = np.array( (i,) )
        elif isinstance(i, np.ndarray):
            a = i
        elif isinstance(i, slice):
            a = np.arange(i.start,i.stop,i.step)
        else:
            raise NotImplementedError
        af = np.floor(a)
        ac = np.ceil(a)
        tmp = []
        for j in range(scipy_interpolator.order[self.kind]):
            tmp.append(af - j)
            tmp.append(ac + j)
        tmp = np.concatenate(tmp)
        return np.union1d(tmp,np.array(())).astype(np.int_)

    def interpolate(self, i, ip, vp, axis):
        if isinstance(i, numbers.Number):
            a = np.array( (i,) )
        elif isinstance(i, np.ndarray):
            a = i
        elif isinstance(i, slice):
            a = np.arange(i.start,i.stop,i.step)
        else:
            raise NotImplementedError
        f = scipy.interpolate.interp1d(ip,vp,axis=axis,kind=self.kind)
        return f(a)