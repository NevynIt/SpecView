import inspect

class autoinit:
    """
    Usage: 
        @autoinit(parameters)
        parameters are:
            prebase = { "attribute name": value to be set before initialising base classes, ...}
            base = True -> call __init__ on super(...) with no parameters, "method name" -> call the method with all parameters given to init (the method is supposed to init the base class)
            bindable = { "bindable attribute name": default value, ...}
            cached = { "cached attribute name": ("name of bindable attribute whose update invalidates the cache", ...), ... }
                NOTE: there has to be a method with the same name of the cached attribute, with no parameters, which is used to calculate the cached value upon update of the dependencies
            triggers = { "bindable or cached attribute name": ("name of method to ba called as soon as the value is updated or invalidated", ...), ... }
                NOTE: the method is called with no parameters, after the update/invalidation is done
            pre = { "attribute name": value to be set before calling __init__, ...}
            post = { "attribute name": value to be set after calling __init__, ...}
        NOTE: The order of the parameters here is the order in which things are applied to the class
    """

    class binding_helper_instance:
        def __init__(self, owner):
            object.__setattr__(self, "owner", owner)

        def _set_attribute(self, name, value):
            object.__setattr__(self, name, value)

        # in order to get the cached attributes working, the whole chain has to be stuff that supports triggers (i.e. bound attribs or cached ones)
        # def __getattr__(self, name):
        #     #this is called only if the object is not in __dict__
        #     return autoinit.binding_reference(self.owner, name)
        
        def __setattr__(self, name, value):
            object.__getattribute__(self, name).binding = value

    class bound_attribute:
        @property
        def value(self):
            raise NotImplementedError

    # class binding_reference(bound_attribute):
    #     def __init__(self, owner, name):
    #         self.owner = owner
    #         self.name = name
        
    #     @property
    #     def value(self):
    #         return getattr(self.owner, self.name)

    class bindable_attribute(bound_attribute):
        def __init__(self, default = None):
            self.triggers = {}
            self.target = self.default = default
            self.bound = False

        def add_trigger(self, fnc, key=None):
            if key == None:
                key = id(fnc)
            self.triggers[key] = fnc

        def del_trigger(self, key):
            del self.triggers[key]

        def call_triggers(self):
            for fnc in self.triggers.values():
                fnc()

        @property
        def value(self):
            if self.bound:
                return self.target.value
            else:
                return self.target

        @value.setter
        def value(self, v):
            if self.bound:
                self.target.value = v
            else:
                self.target = v
            self.call_triggers()

        @property
        def binding(self):
            if self.bound:
                return self.target
            else:
                return None
        
        def check_circular_binding(self, tgt):
            if tgt is self:
                #TODO: use a different exception type
                raise AttributeError("Circular binding")
            if self.bound:
                self.target.check_circular_binding(tgt)

        @binding.setter
        def binding(self, value):
            if value is self:
                raise AttributeError("Circular binding")
            elif value == None:
                #resets to default
                if self.bound == True:
                    self.target.del_trigger(id(self))
                self.bound = False
                self.target = self.default
            elif issubclass(type(value), autoinit.bound_attribute):
                value.check_circular_binding(self)
                self.bound = True
                self.target = value
                self.target.add_trigger(self.call_triggers, id(self))
            else:
                if self.bound == True:
                    self.target.del_trigger(id(self))                
                self.bound = False
                self.target = value
            self.call_triggers()

    class cached_attribute(bound_attribute):
        def __init__(self, actual_get):
            self.targets = []
            self.triggers = {}
            self.calculate = actual_get
            self.cache = None
            self.valid = False

        def add_target(self, tgt):
            self.targets.append(tgt)

        def add_trigger(self, fnc, key=None):
            if key == None:
                key = id(fnc)
            self.triggers[key] = fnc

        def del_trigger(self, key):
            del self.triggers[key]

        def call_triggers(self):
            for fnc in self.triggers.values():
                fnc()

        def invalidate(self):
            self.valid = False
            self.cache = None
            self.call_triggers()

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
            for target in self.targets:
                target.check_circular_binding(tgt)

    class bound_descriptor:
        def __init__(self, name):
            self.name = name

        def __get__(self, instance, owner):
            return getattr(instance._bound, self.name).value
        
        def __set__(self, instance, value):
            getattr(instance._bound, self.name).value = value

    @classmethod
    def multi_setattr(self, obj, attrs):
        for k in attrs:
            setattr(obj,k,attrs[k])

    def __init__(self, *, prebase=None, base=True, bindable=None, cached=None, triggers=None, pre=None, post=None):
        self.prebase = prebase
        self.base = base
        self.bindable = bindable
        self.cached = cached
        self.triggers = triggers
        self.pre = pre
        self.post = post

    def __call__(self,cl):
        def default__autoinit_base__(self, *args, **kwargs):
            super(cl,self).__init__(self)
        
        if self.base == True:
            base_init = default__autoinit_base__
        elif type(self.base) == str:
            base_init = getattr(cl, self.base)
        else:
            base_init = None

        class_init = cl.__init__

        #check if the init function was actually inherited and thus irrelevant
        mro = inspect.getmro(cl)
        if cl.__init__ is mro[1].__init__:
            class_init = None

        for name in self.bindable:
            setattr(cl, name, autoinit.bound_descriptor(name))
        
        for name in self.cached:
            setattr(cl,name + "__actual_get", getattr(cl,name))
            setattr(cl,name, autoinit.bound_descriptor(name))

        def __init__instance__(instance, *args, **kwargs):
            if self.prebase != None:
                autoinit.multi_setattr(instance,self.prebase)
            if base_init != None:
                base_init(instance, *args, **kwargs)
            if self.bindable != None:
                instance._bound = getattr(instance, "_bound", autoinit.binding_helper_instance(instance))
                for name, default_value in self.bindable.items():
                    instance._bound._set_attribute(name,  autoinit.bindable_attribute(default_value))
            if self.cached != None:
                for name, dependencies in self.cached.items():
                    #create the object which cache the value and call the actual get function when needed
                    attr = autoinit.cached_attribute(getattr(instance,name + "__actual_get"))
                    instance._bound._set_attribute(name, attr)
                    if type(dependencies) == str:
                        dependencies = (dependencies, )
                    for dep in dependencies:
                        tgt = getattr(instance._bound, dep)
                        attr.add_target(tgt)
                        tgt.add_trigger(attr.invalidate)
            if self.triggers != None:
                for name, methods in self.triggers.items():
                    if type(methods) == str:
                        methods = (methods, )
                    for method in methods:
                        getattr(instance._bound, name).add_trigger(getattr(instance,method))
            if self.pre != None:
                autoinit.multi_setattr(instance,self.pre)
            if class_init != None:
                class_init(instance, *args, **kwargs)
            if self.post != None:
                autoinit.multi_setattr(instance,self.post)
        
        cl.__init__ = __init__instance__
        return cl

if __name__ == "__main__":
    class baseclass:
        def __init__(self):
            print(f"Base init: {self.__dict__=}")

    @autoinit(
        prebase={
            "prebase_val": 1
        },
        base= "baseinit",
        bindable={
            "bindable_a": 2,
            "bindable_b": 3,
            "bindable_c": 4,
        },
        cached={
            "cached_a_b": ("bindable_a", "bindable_b")
        },
        triggers={
            "bindable_c": "on_bindable_c",
            "cached_a_b": "on_cached_a_b",
        },
        pre={
            "pre_val": 5
        },
        post={
            "post_val": 6
        }
    )
    class test(baseclass):
        # def __init__(self):
        #     print(f"test init: {self.__dict__=}")
        
        def cached_a_b(self):
            return self.bindable_a + self.bindable_b

        def on_bindable_c(self):
            print(f"bindable_c has changed: {self.bindable_c=}")
        
        def on_cached_a_b(self):
            print(f"cached_a_b has changed: {self.cached_a_b=}")
            pass

        def baseinit(self):
            print(f"before baseclass init: {self.__dict__=}")
            baseclass.__init__(self)
            print(f"after baseclass init: {self.__dict__=}")

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