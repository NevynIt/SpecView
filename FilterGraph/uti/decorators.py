import weakref

class autoinit:
    """
    Usage: 
        @autoinit(parameters)
        class ...

        if __autoinit_base__ is defined, it will be called to initialize base classes, and then removed from the class
    """

    class binding_helper_instance:
        def __init__(self, owner):
            self.owner = owner

        def __set_attribute(self, name, value):
            object.__setattr__(self, name, value)

        def __getattr__(self, name):
            #this is called only if the object is not in __dict__
            return bound_attribute(owner, name)
        
        def __setattr__(self, name, value):
            object.__getattribute__(self, name).binding = value

    class bound_attribute:
        def __init__(self, owner, name):
            self.owner = owner
            self.name = name
        
        @property
        def value(self):
            return getattr(self.owner, self.name)

    class bindable_attribute(bound_attribute):
        def __init__(self, default = None):
            self.triggers = weakref.WeakValueDictionary()
            self.target = self.default = default
            self.bound = False

        def add_trigger(fnc, key=None):
            if key == None:
                key = id(fnc)
            self.triggers[key] = fnc

        def del_trigger(key):
            del self.triggers[key]

        def call_trigger():
            for fnc in self.triggers.values:
                fnc()


        @property
        def value(self):
            if self.bound:
                return self.target.value
            else:
                return self.target

        @property.setter
        def value(self, v):
            if self.bound:
                self.target.value = v
            else:
                self.target = v
            self.call_trigger()

        @property
        def binding(self):
            if self.bound:
                return self.target
            else:
                return None
        
        @property.setter
        def binding(self, value):
            if value == None:
                if self.bound == True:
                    self.bound = False
                    self.target = self.default
            elif issubclass(type(value), autoinit.bound_attribute):
                self.bound = True
                self.target = value
            else:
                self.bound = False
                self.target = value
            self.call_trigger()

    @classmethod
    def multi_setattr(obj,attrs):
        for k in attrs:
            setattr(obj,k,attrs[k])

    def __init__(self, *, prebase=None, base=True, bindable=None, triggers=None, pre=None, post=None):
        self.prebase = prebase
        self.base = base
        self.bindable = bindable
        self.triggers = triggers
        self.pre = pre
        self.post = post

    def __call__(self,cl):
        def default__autoinit_base__(self, *args, **kwargs):
            super(cl,self).__init__(self)
        
        if self.base == True:
            if hasattr(cl,"__autoinit_base__"):
                base_init = cl.__autoinit_base__
                #remove autoinit_base so that it is not called again in subclasses
                del cl.__autoinit_base__
            else:
                base_init = default__autoinit_base__
        elif hasattr(cl,"__autoinit_base__"):
            #send out some kind of warning!
            print("WARNING: autoinit decorator found __autoinit_base__ without base==True. This could cause problems in subclasses.")

        class_init = cl.__init__

        for name in self.bindable:
            setattr(cl,name) = property(
                fget = (lambda self: getattr(self._bound,name).value),
                fset = (lambda self, value: getattr(self._bound,name).value = value)
                )

        def __init__instance__(instance, *args, **kwargs)
            if self.prebase != None:
                autoinit.multi_setattr(instance,self.prebase)
            if self.base == True:
                self.base_init(cl, instance, *args, **kwargs)
            if self.bindable != None:
                instance._bound = getattr(instance, "_bound", binding_helper_instance(instance))
                for name, default_value in self.bindable.items():
                    instance._bound.__set_attribute(name,  bindable_attribute(self, name, default_value))
            if self.triggers != None:
                for name, methods in self.triggers.items():
                    if type(methods) == str:
                        methods = (methods, )
                    for method in methods:
                        getattr(instance._bound, name).add_trigger(getattr(instance,method))
            if self.pre != None:
                autoinit.multi_setattr(instance,pre)
            self.class_init(instance, *args, **kwargs)
            if self.post != None:
                autoinit.multi_setattr(instance,self.post)
        
        return __init__instance__

if __name__ == "__main__":
    @autoinit(
        post={
            "name": "my test name"
        },
        bindable={
            "p_in": None,
            "p_aname": "noname",
            "p_jack": 12
        }
    )
    class test:
        pass

    t1 = test1
    t2 = test2
    t2._bind.p_aname = t1._bind.name
    t2._bind.p_in = 55
    t2.p_jack = 43
    print(t2.p_aname)
    print(t2.p_in)
    print(t2.p_jack)