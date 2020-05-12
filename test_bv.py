from bv import BernsteinVaziraniSolver
from dj import DeutschJozsaSolver
import time
n = 6

def f(x, a_str, b_str, nbits):
    a = int(a_str, 2)
    b = int(b_str, 2)
    ax = format((x & a), '0'+str(nbits)+'b').count('1') % 2
    return (ax + b) % 2

def f_1(x):
    return f(x, '110010', '1', n)

def f_2(x):
    return f(x, '101100', '0', n)

start_time = time.time()
a, b = BernsteinVaziraniSolver(n,f_1).run(1,isQC = True)
print("--- %s seconds ---" % (time.time() - start_time))
print(f"f_1 = {a} * x + {b}")

start_time = time.time()
isconst = DeutschJozsaSolver(n,f_2).run(1,isQC = True)
print("--- %s seconds ---" % (time.time() - start_time))
print(f"f_2 is Constant? {bool(isconst)}")