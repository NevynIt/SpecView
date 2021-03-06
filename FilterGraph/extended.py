from FilterGraph.ndfield import ndfield
from FilterGraph.axis_transform import axis_transform
from FilterGraph.axes import axis_info
import numpy as np
import contextvars

#TODO: detect and optimise for obvious cases, and support slices directly
desired_indexes = contextvars.ContextVar("desired_indexes")
selector = contextvars.ContextVar("selector")
inverse = contextvars.ContextVar("inverse")

class extended(axis_transform):
    #possible values are zeros, reflect, nearest, repeat
    def __init__(self, wrapped: ndfield, axes: int or set = None, mode: str = "zeros"):
        super().__init__(wrapped=wrapped, axes=axes)
        self.fill_mode = mode

    def transform_axis(self, axis: axis_info, i):
        return axis_info(
            size=np.inf,
            lbound=-np.inf,
            ubound=np.inf,
            unit=axis.unit,
            annotations=(f"extended({self.fill_mode})", ) + axis.annotations
         )

    def axis_identify_indexes(self, di, axis_n):
        "return indexes that are aligned with the boundaries of axis.index_domain - limited to whole numbers for now"
        di = self.to_index_array(di, axis_n)
        fm = self.fill_mode
        domain = self.wrapped.axes[axis_n].update_slice()

        if fm == "throw":
            if ((di < domain.start) | (di >= domain.stop)).any():
                raise IndexError
            return di
        elif fm == "zeros":
            desired_indexes.set(di)
            sel = (di >= domain.start) & (di < domain.stop)
            selector.set(sel)
            selected = di[sel]
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
            selected = (domain.start + ((di-domain.start) % (domain.stop-domain.start)))
        else:
            raise NotImplementedError
        res, inv = np.unique(selected, return_inverse=True) #TODO: remove the unique call (and subsequent inverse)
        inverse.set(inv)
        return res

    def axis_calculate_values(self, rv, axis_n):
        "return values for all the desired_indexes"
        #use the reconstruction array to get the unbounded values
        res = rv
        
        inv = inverse.get(None)
        if inv is None:
            return res

        if len(res) > 0:
            res = np.take(res, inv, axis_n)

        if self.fill_mode == "zeros":
            di = desired_indexes.get()
            sel = selector.get()

            tmpshape = list(rv.shape)
            tmpshape[axis_n] = len(di)
            tmp = np.zeros(tmpshape, rv.dtype)
            ind = [np.s_[:]] * len(rv.shape)
            ind[axis_n] = sel
            tmp[tuple(ind)] = res
            res = tmp
        return res