from FilterGraph.axis_transform import axis_transform
from FilterGraph.axes import axis_info

class coordspace(axis_transform):
    def transform_axis(self, axis: axis_info): #TODO: TESTME
        cs = axis.coord_slice
        return axis_info(
            origin = 0,
            step = 1,
            steps_forwards = cs.stop,
            steps_backwards = -cs.start,
            unit = axis.unit,
            annotations = ("coordspace", ) + axis.annotations
        )

    def axis_identify_indexes(self, di, axis_n):
        return self.wrapped.axes[axis_n].to_index(di)