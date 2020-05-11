import itertools
import numpy as np
import pyquil.api as api
from pyquil.gates import *
from pyquil.quil import Program

def qubit_strings(n):
    qubit_strings = []
    for q in itertools.product(['0', '1'], repeat=n):
        qubit_strings.append(''.join(q))
    return qubit_strings

def black_box_map(n, a):
    """
    Black-box map, f(x) = x.a for all vectors x, given a
    """
    qubs = qubit_strings(n)
    # calculate each dot product x.a and store in a dict
    d_blackbox = {}
    for q in qubs:
        dot_prod = 0
        for i, xx in enumerate(q):
            dot_prod += a[i] * int(xx)
        d_blackbox[q] = dot_prod % 2

    return d_blackbox

def qubit_ket(qub_string):
    """
    Form a basis ket out of n-bit string specified by the input 'qub_string', e.g.
    '001' -> |001>
    """
    e0 = np.array([[1], [0]])
    e1 = np.array([[0], [1]])
    d_qubstring = {'0': e0, '1': e1}

    # initialize ket
    ket = d_qubstring[qub_string[0]]
    for i in range(1, len(qub_string)):
        ket = np.kron(ket, d_qubstring[qub_string[i]])
    
    return ket

def projection_op(qub_string):
    """
    Creates a projection operator out of the basis element specified by 'qub_string', e.g.
    '101' -> |101> <101|
    """
    ket = qubit_ket(qub_string)
    bra = np.transpose(ket)  # all entries real, so no complex conjugation necessary
    proj = np.kron(ket, bra)
    return proj

def black_box(n, a):
    """
    Unitary representation of the black-box operator on (n+1)-qubits, given the vector a
    """
    d_bb = black_box_map(n, a)
    # initialize unitary matrix
    N = 2**(n+1)
    unitary_rep = np.zeros(shape=(N, N))
    # populate unitary matrix
    for k, v in d_bb.items():
        unitary_rep += np.kron(projection_op(k), np.eye(2) + v*(-np.eye(2) + np.array([[0, 1], [1, 0]])))
        
    return unitary_rep

p = Program()

# pick numer of control qubits to be used
n = 5

# pick a random value for the vector 'a'
a = np.random.randint(low=0, high=2, size=n)
print ("This is the (randomly chosen) value of a: ", a)

# Define U_f
p.defgate("U_f", black_box(n, a))

# Prepare the starting state |0>^(\otimes n) x (1/sqrt[2])*(|0> - |1>)
for n_ in range(1, n+1):
    p.inst(I(n_))
p.inst(X(0))
p.inst(H(0))

# Apply H^(\otimes n)
for n_ in range(1, n+1):
    p.inst(H(n_))
    
# Apply U_f
p.inst(("U_f",) + tuple(range(n+1)[::-1]))

# Apply final H^(\otimes n)
for n_ in range(1, n+1):
    p.inst(H(n_))
    
# Final measurement
classical_regs = list(range(n))
for i, n_ in enumerate(list(range(1, n+1))[::-1]):
    p.measure(n_, classical_regs[i])
    
qvm = api.QVMConnection()
measure_n_qubits = qvm.run(p, classical_regs)

# flatten out list
measure_n_qubits = [item for sublist in measure_n_qubits for item in sublist]

print ("This is the measured values of the first %s qubits at the end: " %n, measure_n_qubits)