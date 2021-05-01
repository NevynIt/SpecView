from .axes import *
import scipy

class scipy_interpolator(interpolator_base):
    "uses interp1d from numpy, assumes a discrete field"

    def find_indexes(self, i):
        pass

    def interpolate(self, i, ip, vp):
        pass