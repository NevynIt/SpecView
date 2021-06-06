from numpy.lib.arraysetops import isin
from FilterGraph.axis_transform import axis_transform
from FilterGraph.axes import axis_info, linear_axis_info

class coordspace(axis_transform):
    def transform_axis(self, axis: axis_info, i): #TODO: TESTME
        cs = axis.to_coord(slice(None))
        return axis_info(
            size = axis.size,
            lbound = cs.start,
            ubound = cs.stop - cs.step,
            unit = axis.unit,
            annotations = ("coordspace", ) + axis.annotations,
           )

    def axis_identify_indexes(self, di, axis_n):
        return self.wrapped.axes[axis_n].to_index(di)