import types

#TODO: 
#       implement chain of reactive property to ensure at run time that the observable properties on which a cacheable depend on are always reactive
#       when a cached is created or alerted that a property has been modified, it should also check all deps are reactive
#       A bound property is not reactive if it is bound to a non-reactive observable
#       getattr of a store should also be updated to return a non reactive observable bound to any attribute of the same instance the store is linked to
#       update the hierarchy to make the observable -> reactive -> bindable|cached

__all__ = ("property_store", "trigger", "call", "assign")

class observable:
    class instance_helper:
        def __init__(self, descriptor):
            self._value = descriptor.default_value
        
        def init_instance(self, descriptor, instance):
            pass

        @property
        def value(self):
            return self._value
        
        @value.setter
        def value(self, v):
            self._value = v

        def check_circular_binding(self, tgt):
            pass

        @property
        def reactive(self):
            return false

    def __init__(self, default_value = None, *, store = None, readonly = False):
        self.store = store
        self.default_value = default_value
        self.readonly = readonly
    
    def __set_name__(self, owner, name):
        self.name = name
        self.store.slots[name] = self

    def __get__(self, instance, owner=None):
        if instance == None:
            return self
        store = getattr(instance, self.store.name)
        slot = getattr(store, self.name)
        return slot.value

    def __set__(self, instance, value):
        if self.readonly:
            raise AttributeError(f"Property {self.name} is readonly")
        store = getattr(instance, self.store.name)
        slot = getattr(store, self.name)
        slot.value = value

class property_store:
    class attribute_reference(observable.instance_helper):
        def __init__(self, instance, name):
            #no need to call the base class
            self.instance = instance
            self.name = name

        def init_instance(self, descriptor, instance):
            raise RuntimeError

        @property
        def value(self):
            return getattr(self.instance, self.name)
        
        @value.setter
        def value(self, v):
            setattr(self.instance, self.name, v)

        def check_circular_binding(self, tgt):
            if tgt is self:
                #TODO: use a different exception type
                raise AttributeError("Circular binding")
            descriptor = getattr(type(self.instance),self.name, None)
            if isinstance(descriptor, observable):
                store = getattr(self.instance, descriptor.store.name)
                slot = getattr(store, self.name)
                slot.check_circular_binding(tgt)

        @property
        def reactive(self):
            return False

    class instance_helper:
        def create_slots(self, descriptor):
            for k, v in descriptor.slots.items():
                vars(self)[k] = type(v).instance_helper(v)

        def init_slots(self, descriptor, instance):
            vars(self)["_instance"] = instance
            for k, v in descriptor.slots.items():
                getattr(self, k).init_instance(v, instance)

        def __getattr__(self, name):
            #Update to return a non reactive bound to instance.name
            return property_store.attribute_reference(self._instance, name)

        def __setattr__(self, name, value):
            if isinstance(getattr(self, name), bindable.instance_helper):
                getattr(self, name).binding = value
            else:
                raise AttributeError(f"{name} is not a bindable property")

    def __init__(self):
        self.name = None
        self.slots = {}

    def __get__(self, instance, owner=None):
        if instance == None:
            return self
        if not self.name in vars(instance):
            store = property_store.instance_helper()
            vars(instance)[self.name] = store
            store.create_slots(self)
            store.init_slots(self, instance)
        return vars(instance)[self.name]
    
    def __set_name__(self, owner, name):
        if self.name != None:
            raise RuntimeError
        self.name = name
    
    def observable(self, *args, **kwargs):
        return observable(*args, **kwargs, store=self)
    
    def reactive(self, *args, **kwargs):
        return reactive(*args, **kwargs, store=self)
    
    def bindable(self, *args, **kwargs):
        return bindable(*args, **kwargs, store=self)
    
    def cached(self, *args, **kwargs):
        "returns a decorator that creates a cached property that is invalidated when any of the observables passed as arguments is modified"
        return cached(*args, **kwargs, store=self)

class reactive(observable):
    class instance_helper(observable.instance_helper):
        def __init__(self, descriptor):
            super().__init__(descriptor)
            self.observers = {}
        
        def init_instance(self, descriptor, instance):
            for v in descriptor.observers.values():
                self.add_observer(types.MethodType(v, instance))

        @property
        def value(self):
            return self._value
        
        @value.setter
        def value(self, v):
            self._value = v
            self.alert()

        def check_circular_binding(self, tgt):
            pass

        def add_observer(self, fnc, key=None):
            if key == None:
                key = id(fnc)
            self.observers[key] = fnc

        def del_observer(self, key):
            del self.observers[key]

        def alert(self):
            for fnc in self.observers.values():
                fnc()

        @property
        def reactive(self):
            return True

    def __init__(self, default_value = None, *, store = None, readonly = False):
        super().__init__(default_value=default_value,store=store, readonly=readonly)
        self.observers = {}

    def add_observer(self, fnc, key=None):
        if key == None:
            key = id(fnc)
        self.observers[key] = fnc

    def del_observer(self, key):
        del self.observers[key]

class bindable(reactive):
    class instance_helper(reactive.instance_helper):
        def __init__(self, descriptor):
            super().__init__(descriptor)
            self.bound = False
            self.default_value = descriptor.default_value

        @property
        def value(self):
            if self.bound:
                return self._value.value
            else:
                return self._value
        
        @value.setter
        def value(self, v):
            if self.bound:
                self._value.value = v
            else:
                self._value = v
            self.alert()

        @property
        def binding(self):
            if self.bound:
                return self._value
            else:
                return None
        
        def check_circular_binding(self, tgt):
            if tgt is self:
                #TODO: use a different exception type
                raise AttributeError("Circular binding")
            if self.bound:
                self._value.check_circular_binding(tgt)

        @binding.setter
        def binding(self, value):
            if value == None:
                if self.bound == True and self._value.reactive:
                    self._value.del_observer(id(self)) #check it is reactive first
                self.bound = False
                self._value = self.default_value
            elif isinstance(value, observable.instance_helper):
                value.check_circular_binding(self)
                if self.bound == True and self._value.reactive:
                    self._value.del_observer(id(self))
                self.bound = True
                self._value = value
                if self._value.reactive:
                    self._value.add_observer(self.alert, id(self))
            else:
                if self.bound == True and self._value.reactive:
                    self._value.del_trigger(id(self))
                self.bound = False
                self._value = value
            self.alert()

        @property
        def reactive(self):
            if self.bound:
                return self._value.reactive
            return True

class cached(reactive):
    "the class works both as a class and a descriptor"
    class instance_helper(reactive.instance_helper):
        def __init__(self, descriptor):
            super().__init__(descriptor)
            self.valid = False
            self.dependencies = []
        
        def init_instance(self, descriptor, instance):
            super().init_instance(descriptor, instance)
            self.getter = types.MethodType(descriptor.getter, instance)
            for dep in descriptor.dependencies:
                if not isinstance(dep, observable):
                    raise TypeError
                store = getattr(instance, dep.store.name)
                slot = getattr(store, dep.name)
                slot.check_circular_binding(self)
                if not slot.reactive:
                    raise RuntimeError("Cached object dependencies must be reactive")
                slot.add_observer(self.invalidate)
                self.dependencies.append(slot)

        def invalidate(self):
            self.valid = False
            self._value = None
            for dep in self.dependencies:
                if not dep.reactive:
                    raise RuntimeError("Cached object dependencies must stay reactive all the time")
            self.alert()

        @property
        def value(self):
            if not self.valid:
                self.cache = self.getter()
                self.valid = True
            return self.cache

        def check_circular_binding(self, tgt):
            if tgt is self:
                #TODO: use a different exception type
                raise AttributeError("Circular binding")
            for dep in self.dependencies:
                dep.check_circular_binding(tgt)

    def __init__(self, *dependencies, store = None, getter = None, readonly = True):
        super().__init__(store = store, readonly = readonly)
        self.dependencies = dependencies
        self.getter = getter

    def __call__(self, getter):
        self.getter = getter
        return self

def trigger(*args):
    "decorator that binds a call to the method every time the observables in args are modified"
    def decorate(fnc):
        for obs in args:
            if isinstance(obs, reactive):
                obs.add_observer(fnc)
            else:
                raise TypeError
        return fnc
    return decorate

#not sure it's actually useful!
def call(function_to_call, *, args=(), kwargs={}, append=False):
    "decorator that prepends or appends a member function call to the decorated member function, putting args or kwargs to None passes the ones given in the call. always returns the value of the decorated function"
    def decorate(function):
        def decorated_function(self, *inner_args, **inner_kwargs):
            if not append:
                function_to_call(self, *(inner_args if args == None else args), **(inner_kwargs if kwargs == None else kwargs))
            retval = function(self, *inner_args, **inner_kwargs)
            if append:
                function_to_call(self, *(inner_args if args == None else args), **(inner_kwargs if kwargs == None else kwargs))
            return retval
        return decorated_function
    return decorate

#TODO:
# def __base_init(self, *inner_args, **inner_kwargs):
#     super().__init__(*inner_args, **inner_kwargs)

# def baseinit(*, args=(), kwargs={}, append=False):
#     return call(__base_init, args=args, kwargs=kwargs, append=append)

def assign(**kwargs):
    def decorate(fnc):
        def decorated_function(self, *inner_args, **inner_kwargs):
            for k,v in kwargs.items():
                setattr(self,k,v)
            return fnc(self,*inner_args, **inner_kwargs)
        return decorated_function
    return decorate

def assignargs(**kwargs):
    raise NotImplementedError

if __name__ == "__main__":
    class baseclass:
        def __init__(self):
            print(f"Base init: {self.__dict__=}")

    class test(baseclass):
        _bound = property_store()
        bindable_a = _bound.bindable(2)
        bindable_b = _bound.bindable(3)
        bindable_c = _bound.bindable(4)

        def baseinitial(self):
            print(f"before baseclass init: {self.__dict__=}")
            baseclass.__init__(self)
            print(f"after baseclass init: {self.__dict__=}")

        @assign(prebase_val = 1)
        @call(baseinitial)
        # @baseinit()
        @assign(pre_val = 5)
        def __init__(self):
            print(f"test init: {self.__dict__=}")
        
        @_bound.cached(bindable_a, bindable_b)
        def cached_a_b(self):
            return self.bindable_a + self.bindable_b

        @trigger(bindable_c)
        def on_bindable_c(self):
            print(f"bindable_c has changed: {self.bindable_c=}")
        
        @trigger(cached_a_b)
        def on_cached_a_b(self):
            print(f"cached_a_b has changed: {self.cached_a_b=}")
            pass

    t1 = test()
    t2 = test()
    try:
        t1.cached_a_b = 1234
        print("Exception missed!")
    except Exception as e:
        print(f"Readonly as expected {e=}") 

    t2._bound.bindable_b = t1._bound.cached_a_b
    t1.bindable_a = 5
    t1.bindable_c = 9
    t1._bound.bindable_a = t1._bound.bindable_b
    t1._bound.bindable_b = t1._bound.bindable_c
    t1._bound.bindable_c = t2._bound.bindable_a
    
    try:
        t1._bound.bindable_c = property_store.attribute_reference(t1, "bindable_a")
        print("Exception missed!")
    except Exception as e:
        print(f"Circular as expected {e=}") 


    try:
        t2._bound.bindable_a.binding = t2._bound.bindable_b #this should raise a circular binding exception
        print("Exception missed!")
    except Exception as e:
        print(f"Circular as expected {e=}") 

    try:
        t1._bound.bindable_b = t2._bound.pre_val
        print("Exception missed!")
    except Exception as e:
        print(f"Ractive as expected {e=}") 
    
    try:
        t2._bound.bindable_a.binding = property_store.attribute_reference(t2, "bindable_b")
        print("Exception missed!")
    except Exception as e:
        print(f"Ractive as expected {e=}") 
