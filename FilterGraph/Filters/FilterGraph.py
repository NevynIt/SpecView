from ..Filter import Filter

class FGFactory:
    raise NotImplementedError
    
    @classmethod
    def serialize(inst):
        # restituisce un oggetto (numero, stringa, dict, tuple/list, combinazioni)
        pass

    @classmethod
    def deserialize(inst, store):
        # store é un JSON o un oggetto (numero, stringa, dict, tuple/list, combinazioni)
        pass

    @classmethod
    def create_factory(inst):
        # should identify loops and create a warning
        pass

    class AttributeProxy:
        def __init__(self, self_proxy, name):
            pass

    class SubFilterProxy:
        def __init__(self, root, classref):
            self.name = None
            pass

        def __setattr__(self, name, value):
            # se qualcosa é giá stato assegnato da errore
            # se value é un attribute proxy si segna che deve fare un binding
            # se value é (numero, stringa, dict, tuple/list, combinazioni) si segna un parametro di configurazione
            pass

    def __call__(self, classref):
        # se arg é una classe di tipo filter o una factory, return SubFilterProxy(self, classref)
        pass
    
    def __getattr__(self, name):
        # se il nome é di una cosa da creare restituisce il subfilterproxy
        # altrimenti return un attributeproxy riferito al filtergraph radice
        pass

    def __setattr__(self, name, value):
        # se qualcosa é giá stato assegnato da errore
        # se value é un SubFilterProxy senza nome segna che lo deve creare con quel nome (e glielo da)
        # se value é un attribute proxy si segna che deve fare un binding
        # se value é (numero, stringa, dict, tuple/list) si segna un parametro di configurazione con quel nome
        pass

class FilterGraph(Filter):
    raise NotImplementedError