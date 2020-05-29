# importing necessary package
import numpy as np
import math
from qiskit import QuantumCircuit, execute, Aer
from qiskit.quantum_info.operators import Operator

# Generate the qubit string from 0 to 2^n with leading zeros
def get_qstring(n):
    return [format(q, '0'+ str(n) + 'b') for q in range(0, 2**n)]

class BernsteinVaziraniSolver(object): 
    # Constructor
    def __init__(self, num_qubits, f):
        self.__num_qubits = num_qubits
        self.__f = f
        self.__b = f(0)
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
        print(p.draw())
        print(p.draw(output="latex_source"))
        self.__circuit = p

    def run(self, trials):
        simulator = Aer.get_backend("qasm_simulator")
        job = execute(self.__circuit, simulator, shots=trials)
        result = job.result().get_counts()
        most_common = [k for k, v in sorted(result.items(), key=lambda item: item[1])][-1]
        return most_common, self.__b

n = 6

def f(x, a_str, b_str, nbits):
    a = int(a_str, 2)
    b = int(b_str, 2)
    ax = format((x & a), '0'+str(nbits)+'b').count('1') % 2
    return (ax + b) % 2

def f_1(x):
    return f(x, '110101', '1', n)

a, b = BernsteinVaziraniSolver(n,f_1).run(1000)
print(f"function = {a} * x + {b}")