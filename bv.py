import itertools
import numpy as np
import pyquil.api as api
from pyquil.gates import X, H
from pyquil import Program, get_qc

# Generate the qubit string from 0 to 2^n with leading zeros
def get_qstring(n):
    return [format(q, '0'+ str(n) + 'b') for q in range(0, 2**n)]

# Generate the bit mapping between inputs and output
# f(x) = x.a
def gen_mapping(n, a):
    qstr = get_qstring(n)
    num_a = int(''.join([str(i) for i in a]), 2)
    # calculate each dot product x.a and store in a dict
    d_mapping = {}
    for q in qstr:
        res = format((int(q, 2) & num_a), '0'+str(n)+'b').count('1') % 2
        d_mapping[q] = res
    return d_mapping

# Generate Uf
def gen_Uf(n, a):
    """
    generate the unitary matrix of the black-box operator on (n+1)-qubits
    bit string -> 1, f(x) add b % 2 will flip, where matrix is 
         [[0, 1]
          [1, 0]]
    bit string -> 0, f(x) add b % 2 remain same, where matrix is
         [[1, 0]
          [0, 1]]    
    """
    mapping = gen_mapping(n, a)
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

# pick a random value for the vector 'a'
a = np.random.randint(low=0, high=2, size=n)
print ("This is the (randomly chosen) value of a: ", a)

# Define the Quantum Computer and set the time output
qc = get_qc(str(n+1)+"q-qvm")
qc.compiler.client.timeout = 1000

# Define the program
p = Program()

# Define U_f
p.defgate("U_f", gen_Uf(n, a))

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
results = qc.run_and_measure(p, trials=5)

# Measure all bits
del results[0]
measured_results = [s for k, v in results.items() for s in set(v)][::-1]
print("This is the measured value of a: ", measured_results)