import types

class property_store:
    class instance_helper:
        def __init__(self, descriptor, instance):
            for k, v in descriptor.slots:
                setattr(self, k, type(v).instance_helper(v, instance))

    def __init__(self):
        self.name = None
        self.slots = {}

    def __get__(self, instance, owner=None):
        if not self.name in vars(instance):
            vars(instance)[self.name] = property_store.instance_helper(self, instance)
        return vars(instance)[self.name]
    
    def __set_name__(self, owner, name):
        if self.name != None:
            raise RuntimeError
        self.name = name
    
    def observable(self, default_value = None):
        return observable(default_value, self)
    
    def bindable(self, default_value = None):
        return bindable(default_value, self)
    
    def cached(self, *args, getter = None):
        "returns a decorator that creates a cached property that is invalidated when any of the observables passed as arguments is modified"
        return cached(self, *args, getter = None)

class observable:
    class instance_helper:
        def __init__(self, descriptor, instance):
            self._value = descriptor.default_value
            self.observers = []
            for k, v in descriptor.observers:
                self.observers[k] = types.MethodType(v, instance)

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

    def __init__(self, store, default_value = None):
        self.store = store
        self.default_value = default_value
        self.observers = []
    
    def __set_name__(self, owner, name):
        self.name = name
        self.store.slots[name] = self

    def __get__(self, instance, owner=None):
        store = getattr(instance, self.store.name)
        slot = getattr(store, self.name)
        return slot.value

    def add_observer(self, fnc, key=None):
        if key == None:
            key = id(fnc)
        self.observers[key] = fnc

    def del_observer(self, key):
        del self.observers[key]

    def __set__(self, instance, value):
        store = getattr(instance, self.store.name)
        slot = getattr(store, self.name)
        slot.value = v

class bindable(observable):
    class instance_helper(observable.instance_helper):
        def __init__(self, descriptor, instance):
            super().__init__(descriptor, instance)
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
                if self.bound == True:
                    self._value.del_observer(id(self))
                self.bound = False
                self._value = self.default_value
            elif isinstance(value, observable):
                value.check_circular_binding(self)
                if self.bound == True:
                    self._value.del_observer(id(self))                
                self.bound = True
                self._value = value
                self._value.add_observer(self.alert, id(self))
            else:
                if self.bound == True:
                    self._value.del_trigger(id(self))                
                self.bound = False
                self._value = value
            self.alert()

class cached(observable):
    "the class works both as a class and a descriptor"
    class instance_helper(observable.instance_helper):
        def __init__(self, descriptor, instance):
            super().__init__(descriptor, instance)
            self.valid = False
            self.dependencies = []
            for dep in descriptor.dependencies:
                if not isinstance(dep, observable):
                    raise TypeError
                store = getattr(instance, dep.store.name)
                slot = getattr(store, dep.name)
                slot.check_circular_binding(self)
                slot.add_observer(self.invalidate)
                self.dependencies.append(slot)

        def invalidate(self):
            self.valid = False
            self._value = None
            self.alert()

        @property
        def value(self):
            if not self.valid:
                self.cache = self.calculate()
                self.valid = True
            return self.cache

        def check_circular_binding(self, tgt):
            if tgt is self:
                #TODO: use a different exception type
                raise AttributeError("Circular binding")
            for dep in self.dependencies:
                dep.check_circular_binding(tgt)

    def __init__(self, store, *dependencies, getter = None):
        super().__init__(store)
        self.dependencies = dependencies
        self.getter = getter

    def __call__(self, getter):
        self.getter = getter
        return self

def trigger(*args):
    "decorator that binds a call to the method every time the observables in args are modified"
    def decorate(fnc):
        for obs in args:
            if isinstance(obj, observable):
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
    return decorate

def __base_init(self, *inner_args, **inner_kwargs):
    super().__init__(*inner_args, **inner_kwargs)

def baseinit(*, args=(), kwargs={}, append=False):
    return call(__base_init, args=args, kwargs=kwargs, append=append)

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

        @assign(dict(
            prebase_val = 1
        ))
        @call(baseinitial)
        @baseinit
        @assign(dict(
            pre_val = 5
        ))
        @assign(dict(
            post_val = 6
        ), append = True)
        def __init__(self):
            print(f"test init: {self.__dict__=}")
        
        @cached(bindable_a, bindable_b)
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
    t2._bound.bindable_b = t1._bound.cached_a_b
    t1.bindable_a = 5
    t1.bindable_c = 9
    t1._bound.bindable_a = t1._bound.bindable_b
    t1._bound.bindable_b = t1._bound.bindable_c
    t1._bound.bindable_c = t2._bound.bindable_a
    try:
        t2._bound.bindable_a = t2._bound.bindable_b #this should raise a circular binding exception
    except AttributeError:
        print("Exception as expected")