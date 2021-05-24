# import class_definition_helpers as cdh
# from FilterGraph.axes import axis_info, domain

# class sampled_axis(axis_info):
#     """
#     axis_domain must be a constant or reactive property, returning a sampled or discrete and bounded domain
#     index_domain and the transform functions are automatically generated
#     """

#     props = cdh.property_store()
#     axis_domain = props.reactive( )

#     @props.cached(axis_domain)
#     def index_domain(self):
#         # assert self.axis_domain == None, "axis_domain is None"
#         # assert self.axis_domain.nsamples == None or self.axis_domain.nsamples == np.inf, "axis_domain is not sampled nor discrete or not bounded"
#         return domain(0, self.axis_domain.nsamples, 1)

#     def __to_index_impl(self,coords):
#         # assert self.axis_domain == None, "axis_domain is None"
#         # assert self.axis_domain.step, "axis_domain is not sampled nor discrete"
#         # assert self.axis_domain.start > -np.inf, "axis_domain is not bounded"
#         return (coords - self.axis_domain.start)/self.axis_domain.step

#     def to_index(self, x):
#         if isinstance(x, slice):
#             x1 = slice(x.start or self.axis_domain.start, x.stop or self.axis_domain.stop, x.step or self.axis_domain.step)
#             return slice(self.__to_index_impl(x1.start), self.__to_index_impl(x1.stop), x1.step/self.axis_domain.step)
#         else:
#             #this works for scalars or ndarrays of indexes
#             return self.__to_index_impl(x)

#     def __from_index_impl(self,indexes):
#         return self.axis_domain.start + (indexes*self.axis_domain.step)

#     def from_index(self, indexes):
#         if isinstance(indexes, slice):
#             i1 = slice(indexes.start or self.index_domain.start, indexes.stop or self.index_domain.stop, indexes.step or self.index_domain.step)
#             return slice(self.__from_index_impl(i1.start), self.__from_index_impl(i1.stop), i1.step*self.axis_domain.step)
#         else:
#             return self.__from_index_impl(indexes)