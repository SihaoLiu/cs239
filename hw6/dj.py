# importing necessary package
import numpy as np
import math
from qiskit import QuantumCircuit, execute, Aer
from qiskit.quantum_info.operators import Operator

# Generate the qubit string from 0 to 2^n with leading zeros
def get_qstring(n):
    return [format(q, '0'+ str(n) + 'b') for q in range(0, 2**n)]

class DeutschJozsaSolver(object): 
    # Constructor
    def __init__(self, num_qubits, f):
        self.__num_qubits = num_qubits
        self.__f = f
        self.__compute_matrices()
        self.__build_circuit()

    def __compute_matrices(self):
        qstr = get_qstring(self.__num_qubits)
        mapping = {}
        for q in qstr:
            mapping[q] = self.__f(int(q, 2))
        N = 2**(self.__num_qubits+1)
        Uf = np.zeros(shape=(N, N))
        for k, v in mapping.items():
            idx = int(k, 2) * 2
            if v:
                Uf[idx + 1][idx] = 1
                Uf[idx][idx + 1] = 1
            else:
                Uf[idx][idx] = 1
                Uf[idx + 1][idx + 1] = 1
        self.__Uf = Uf
    
    def __build_circuit(self):
        # Initialize the Circuit
        p = QuantumCircuit(self.__num_qubits + 1, self.__num_qubits)

        # Apply Hadamard gate to the first n qubits
        for qubit_idx in range(1, self.__num_qubits + 1):
            p.h(qubit_idx)

        # Set the last bit to |->
        p.x(0)
        p.h(0)

        # Define U_f and Append Uf
        Uf_GATE = Operator(self.__Uf)
        p.append(Uf_GATE, range(self.__num_qubits + 1))

        # Repeat Hadamard gate to the first n qubits
        for qubit_idx in range(1, self.__num_qubits + 1):
            p.h(qubit_idx)

        # measure the qubits
        p.measure(range(1, self.__num_qubits + 1), range(self.__num_qubits))
        #print(p.draw())
        #print(p.draw(output="latex_source"))
        self.__circuit = p

    def run(self, trials):
        simulator = Aer.get_backend("qasm_simulator")
        job = execute(self.__circuit, simulator, shots=trials)
        result = job.result().get_counts()
        most_common = [k for k, v in sorted(result.items(), key=lambda item: item[1])][-1]
        if int(most_common) == 0:
            return False # Const
        else:
            return True # Balanced

# ------------------------- Test case -------------------------

n = 10

def f_balanced(x):
    if x >= 2**(n-1):
        return 1
    else:
        return 0

def f_const(x):
    return 1

import time

# Set the start time
start_time = time.time()
# Initialize the DJ solver and run with 1000 trials
dj_solver = DeutschJozsaSolver(n, f_balanced)
result = ""
if dj_solver.run(1000):
    result = "Balanced"
else:
    result = "Const"
# Calculate the execution time
print("--- %s seconds ---" % (time.time() - start_time))
print(f"function is {result}")

#isbalanced = DeutschJozsaSolver(n,f_balanced).run(1000)
#print(f"f_2 is Balanced? {bool(isbalanced)}")