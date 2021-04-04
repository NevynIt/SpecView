def multi_setattr(self,attrs):
    for k in attrs:
        setattr(self,k,attrs[k])

def autoinit(*, prebase=None, base=True, pre=None, post=None):
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
        
        def new_init(self, *args, **kwargs):
            if prebase != None:
                multi_setattr(self,prebase)
            if base == True:
                base_init(self, *args, **kwargs)
            if pre != None:
                multi_setattr(self,pre)
            old_init(self, *args, **kwargs)
            if post != None:
                multi_setattr(self,post)

        cl.__init__ = new_init
        return cl
    return deco

if __name__ == "__main__":

    class ba:
        def __init__(self):
            self.baaa = 3
            print("init base")

    @autoinit(
        post = {
            "a": 5,
            "b": 8
        },
        pre = {
            "g": 9
        },
        prebase = {
            "t": 6
        },
    )
    class pippo(ba):
        def __autoinit_base__(self, pio = 2):
            print("pippo autoinit base - pre")
            super(pippo,self).__init__()
            print("pippo autoinit base - post")

        def __init__(self, pio = 5):
            print("init pippo")
            self.pi = pio

    p = pippo()
    print(p)

    p = pippo(3)
    print(p)