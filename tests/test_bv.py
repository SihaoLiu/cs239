from bv import BernsteinVaziraniSolver
from dj import DeutschJozsaSolver
import time
n = 5

def f(x, a_str, b_str, nbits):
    a = int(a_str, 2)
    b = int(b_str, 2)
    ax = format((x & a), '0'+str(nbits)+'b').count('1') % 2
    return (ax + b) % 2

def f_1(x):
    return 1#f(x, '00000', '1', n)

start_time = time.time()
a, b = BernsteinVaziraniSolver(n,f_1).run(1,isQC = True)
print("--- %s seconds ---" % (time.time() - start_time))
print(f"f_1 = {a} * x + {b}")

"""

def f_3(x):
    if x < 16:
        return 1
    else:
        return 0

def f_4(x):
    if x < 17 and x >= 1:
        return 1
    else:
        return 0

def f_5(x):
    if x < 32 and x > 16:
        return 1
    else:
        return 0

start_time = time.time()
isconst = DeutschJozsaSolver(n,f_5).run(1,isQC = True)
print("--- %s seconds ---" % (time.time() - start_time))
print(f"f_2 is Constant? {bool(isconst)}")
"""