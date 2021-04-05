import time


class bound_attribute:
    def __init__(self, owner, name, bindable = True):
        self.owner = owner
        self.name = name
        self.target = None
        self.bound = False
        self.bindable = bindable
        # self.lastupdate = time.time()
    
    @property
    def value(self):
        if self.bound:
            return getattr(self.target.owner, self.target.name)
        else:
            return self.target
    
    @property.setter
    def value(self, v):
        # self.lastupdate = time.time()
        if self.bound:
            return setattr(self.target.owner, self.target.name, v)
        else:
            self.target = v
    
    @property
    def binding(self):
        if self.bound:
            return self.target
        else:
            return None
    
    @property.setter
    def binding(self, value):
        if self.bindable:
            if self.value == None and self.bound == false:
                return
            elif self.value == None and self.bound == True:
                self.bound = False
                self.target = None
            elif type(value) == bound_attribute:
                self.bound = True
                self.target = value
            else:
                self.bound = False
                self.target = value
        else:
            raise AttributeError(f"Attribute {self.name} of object {self.owner} is not bindable")

class binding_helper:
    def __init__(self, owner, attrs)
        self.attributes = {}
        self.owner = owner
        for name in attrs:
            self.attributes[name] = bound_attribute(owner, name)
            self.attributes[name].value = attrs[name]

    def __getattr__(self, name):
        return bound_attribute(owner, name, False)


def multi_setattr(self,attrs):
    for k in attrs:
        setattr(self,k,attrs[k])

def autoinit(*, prebase=None, base=True, bindable=None, pre=None, post=None):
    """
    Usage: 
        @autoinit(parameters)
        class ...

        if __autoinit_base__ is defined, it will be called to initialize base classes, and then removed from the class
    """

    def deco(cl):
        def default__autoinit_base__(self, *args, **kwargs):
            super(cl,self).__init__(self)
        
        if base == True:
            if hasattr(cl,"__autoinit_base__"):
                base_init = cl.__autoinit_base__
                #remove autoinit_base so that it is not called again in subclasses
                del cl.__autoinit_base__
            else:
                base_init = default__autoinit_base__
        elif hasattr(cl,"__autoinit_base__"):
            #send out some kind of warning!
            print("WARNING: autoinit decorator found __autoinit_base__ without base==True. This could cause problems in subclasses.")

        old_init = cl.__init__
        
        if bindable != None:
            for name in bindable:

            # add attributes for bound properties here if any

        def new_init(self, *args, **kwargs):
            if prebase != None:
                multi_setattr(self,prebase)
            if base == True:
                base_init(self, *args, **kwargs)
            if bindable != None:
                # add bound properties to binding_helper here if any
                pass
            if pre != None:
                multi_setattr(self,pre)
            old_init(self, *args, **kwargs)
            if post != None:
                multi_setattr(self,post)

        cl.__init__ = new_init
        return cl
    return deco


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