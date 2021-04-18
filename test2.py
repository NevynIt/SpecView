class test:
    n = 0

    def __init__(self):
        print(f"init {test.n}")
        test.n = test.n+1

    def __getitem__(self, *args, **kwargs):
        print(f"getitem {args=} {kwargs=}")
        

    def fnc(self, *args, **kwargs):
        print(f"fnc {args=} {kwargs=}")
    
t =test()

t[1]
t[1:2]
t[1:2:3]
t[1,1]
t["abc":"def":t,1:3]
t[...]
t[...:123:("a","b",),34,12:45:...]
t[()]
t[:]

t.fnc(12, ..., 43)
t.fnc(12, ..., 43, test=33)
t.fnc(slice(1,2,3), test=33)
slice(1,2,3).indices(3)