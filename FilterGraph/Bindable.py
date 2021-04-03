class Bindable:
    default_binding = {}
    auto_attributes = {}

    def __init__(self):
        self.bindings = {}
        for name, value in type(self).auto_attributes.items():
            setattr(self,name,value)
            if name.startswith("m_"):
                self.bind_props("p_"+name[2:],self,name)
        self.bind_props(type(self).default_binding)

    def bind_props(self, name, source = None, remote_name = None):
        if issubclass(type(name),dict):
            for name_here, name_there in name.items():
                self.bind_props(name_here, source, name_there)
        elif issubclass(type(name),list) or issubclass(type(name),tuple):
            for name in name:
                self.bind_props(name, source, name)
        elif issubclass(type(name),str):
            if not name.startswith("p_"):
                raise AttributeError("Bound property names must start with p_")

            #Check if we already have an attribute
            if not name in self.bindings:
                found = True
                try:
                    getattr(self,name)
                except AttributeError:
                    found = False
                if found:
                    raise AttributeError("Bound properties cannot override existing attributes")

            #Fix defalut parameters
            if source == None:
                source = self
            if remote_name == None:
                remote_name = name
            
            #Check circular bindings
            tmpSrc = source
            tmpKey = remote_name
            while issubclass(type(tmpSrc), Bindable) and tmpKey in tmpSrc.bindings:
                tmpSrc, tmpKey = tmpSrc.bindings[tmpKey]
                if tmpSrc is self and tmpKey == name:
                    raise AttributeError("Circular binding")
            
            self.bindings[name] = (source, remote_name)
    
    def unbind_props(self, name):
        if issubclass(type(name),dict):
            for name in name.keys():
                self.unbind_props(name)
        elif issubclass(type(name),list) or issubclass(type(name),tuple):
            for name in name:
                self.unbind_props(name)
        elif issubclass(type(name),str):
            if name in self.bindings:
                del self.bindings[name]
                if name in type(self).default_binding:
                    self.bind_props(name, self, self.__class__.default_binding[name])
                if "m_"+name[2:] in type(self).auto_attributes:
                    self.bind_props(name, self, "m_"+name[2:])

    
    def __getattr__(self, name):
        if not name.startswith("p_"):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        if name in self.bindings:
            return getattr(*self.bindings[name])
        else:
            raise AttributeError(f"'{type(self).__name__}' object at {id(self)} has no bound property '{name}'")
    
    def __dir__(self):
        return set(self.bindings.keys()) | set(object.__dir__(self))

    def __setattr__(self,name,value):
        if name != "bindings" and name in self.bindings:
            setattr(*self.bindings[name],value)
        else:
            return object.__setattr__(self,name,value)