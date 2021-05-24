from FilterGraph.ndfield import ndfield
from FilterGraph.axis_transform import axis_transform
from FilterGraph.axes import axis_info, domain
import scipy.interpolate
import numpy as np
import contextvars
import dataclasses

desired_indexes = contextvars.ContextVar("desired_indexes")
interpolation_indexes = contextvars.ContextVar("interpolation_indexes")

#TODO: detect and optimise for obvious cases, and support slices directly

class interpolated(axis_transform):
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

    def __init__(self, wrapped: ndfield, axes: int or set = None, mode: str = "floor"):
        super().__init__(wrapped=wrapped, axes=axes)
        self.interp_mode = mode

    def transform_axis(self, axis:axis_info):
        return dataclasses.replace(axis,annotations=(f"interpolated({self.interp_mode})", ) + axis.annotations)

    def axis_identify_indexes(self, di, axis_n):
        "return indexes that are aligned with the phase and step of axis.index_domain - limited to whole numbers for now"
        di = self.to_index_array(di, axis_n)
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
        elif im in interpolated.interp_order:
            selector = (di % 1) == 0
            constantset = di[selector]
            interpset = di[~selector]            
            af = np.floor(interpset)
            ac = np.ceil(interpset)            
            tmp = []
            for j in range(interpolated.interp_order[im]):
                tmp.append(af - j)
                tmp.append(ac + j)
            interpset = np.concatenate(tmp)

            desired_indexes.set(di)

            ii = np.union1d(constantset, interpset).astype(np.int_)
            interpolation_indexes.set(ii)

            return ii
        else:
            raise NotImplementedError

    def axis_calculate_values(self, rv, axis_n):
        "return values for all the desired_indexes"
        #use the unbounded values to reconstruct the interpolated values
        im = self.interp_mode
        if im in ("floor", "ceil", "round", "throw"):
            return rv
        elif im in interpolated.interp_order:
            ii = interpolation_indexes.get()
            di = desired_indexes.get()
            f = scipy.interpolate.interp1d(ii,rv,axis=axis_n,kind=im)
            return f(di)
        else:
            raise NotImplementedError