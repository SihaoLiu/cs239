import itertools
import numpy as np
import random
import pyquil.api as api
from pyquil.gates import X, H
from pyquil import Program, get_qc

# Generate the qubit string from 0 to 2^n with leading zeros
def get_qstring(n):
    return [format(q, '0'+ str(n) + 'b') for q in range(0, 2**n)]

# Generate the bit mapping between inputs and output
def gen_mapping(n, isBalance):
    qstr = get_qstring(n)
    # If the function is constant, assign either 1 or 0.
    if not isBalance:
        const = np.random.choice([0, 1])
        bb_map = {q: const for q in qstr}
    else:
    # The function is balanced, randomly pick
        half = np.random.choice(qstr, size=2**(n-1), replace=False)
        bb_map = {q_l : 0 for q_l in qstr}
        bb_map.update({q_r : 1 for q_r in half})
    return bb_map

# Generate Uf
def gen_Uf(n, isBalance):
    """
    generate the unitary matrix of the black-box operator on (n+1)-qubits
    bit string -> 1, f(x) add b % 2 will flip, where matrix is 
         [[0, 1]
          [1, 0]]
    bit string -> 0, f(x) add b % 2 remain same, where matrix is
         [[1, 0]
          [0, 1]]    
    """
    mapping = gen_mapping(n, isBalance=isBalance)
    N = 2**(n+1)
    Uf = np.zeros(shape=(N, N))
    for k, v in mapping.items():
        idx = int(k, 2) * 2
        if v:
            Uf[idx + 1][idx] = 1
            Uf[idx][idx + 1] = 1
        else:
            Uf[idx][idx] = 1
            Uf[idx + 1][idx + 1] = 1
    return Uf

# pick number of control qubits to be used
n = 4

# Define the Quantum Computer and set the time output
qc = get_qc(str(n+1)+"q-qvm")
qc.compiler.client.timeout = 1000

# Define the program
p = Program()

# Define U_f
isBalance = bool(random.getrandbits(1))
p.defgate("U_f", gen_Uf(n, isBalance=isBalance))
print('The function is balance ? ' + str(isBalance))

# Set the helper bit to |->
p.inst(X(0))
p.inst(H(0))

# Apply H to the rest of bits
for n_ in range(1, n+1):
    p.inst(H(n_))

# Apply U_f to bit n+1 -> 1, bit 0 is the helper bit
inst = ("U_f",) + tuple(range(n+1)[::-1])
p.inst(inst)

# Apply final H to the rest of bits
for n_ in range(1, n+1):
    p.inst(H(n_))

# Run and Measure the Quantum Computer
print(to_latex(p))
results = qc.run_and_measure(p, trials=5)
# Measure all bits
del results[0]
sum_bits = 0
for k, v in results.items():
    sum_bits += sum(v)
if not sum_bits:
    print("The function is Constant")
else:
    print("The function is Balanced")
