import numba
import numpy as np
import math
import timeit, functools

#operation: sqrt(x*x + y*y)

def dotest(n):
    x = np.random.rand(n)
    y = np.random.rand(n)
    z = np.empty_like(x)
    for i in numba.prange(x.shape[0]):
        z[i] = math.sqrt(x[i]*x[i] + y[i]*y[i])

def npvers(n):
    x = np.random.rand(n)
    y = np.random.rand(n)
    z = np.sqrt(x*x+y*y)

def timetest(n, reps):
    print(f"{n=} {reps=}")
    f = npvers
    f0 = functools.partial(f, n)
    t0 = timeit.timeit(f0, number=reps)
    print(f"NP: {t0}")

    f = dotest
    f0 = functools.partial(f, n)
    t0 = timeit.timeit(f0, number=reps)
    print(f"BASE: {t0}")

    f1 = functools.partial(numba.jit(nopython = True)(f), n)
    t1 = timeit.timeit(f1, number=reps)
    print(f"JIT: {t1}")

    f1 = functools.partial(numba.jit(nopython = True, parallel=True, nogil=True)(f), n)
    t1 = timeit.timeit(f1, number=reps)
    print(f"Parallel: {t1}")

    # f1 = functools.partial(numba.jit(nopython = True, target="cuda")(f), n)
    # t1 = timeit.timeit(f1, number=reps)
    # print(f"Parallel: {t1/t0}")

timetest(100,100)
timetest(1000000,2)