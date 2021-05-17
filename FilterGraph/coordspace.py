from FilterGraph.axis_transform import axis_transform
from FilterGraph.axes import identity_axis

class coordspace(axis_transform):
    def transform_axis(self, axis):
        ai = identity_axis()
        ai.unit = axis.unit
        ai.annotations = ("coordspace", ) + ai.annotations
        ai.axis_domain = axis.axis_domain

    def axis_identify_indexes(self, di, axis_n):
        return self.wrapped.axes[axis_n].to_index(di)