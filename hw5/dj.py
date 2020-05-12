import itertools
import numpy as np
import pyquil.api as api
from pyquil.gates import X, H
from pyquil import Program, get_qc

# Generate the qubit string from 0 to 2^n with leading zeros
def get_qstring(n):
    return [format(q, '0'+ str(n) + 'b') for q in range(0, 2**n)]

class DeutschJozsaSolver(object): 
    # Constructor
    def __init__(self, num_qubits, f):
        self.__num_qubits = num_qubits
        self.__f = f
        self.__b = f(0)
        self.__instantiate_qubits()
        self.__compute_matrices()
        self.__build_circuit()

    def __instantiate_qubits(self):
        self.__qubits = list(range(self.__num_qubits+1)[::-1])

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
        # Define the program
        p = Program()

        # Define U_f
        p.defgate("U_f", self.__Uf)

        # Set the helper bit to |->
        p.inst(X(0))
        p.inst(H(0))

        # Apply H to the rest of bits
        for n_ in range(1, self.__num_qubits+1):
            p.inst(H(n_))

        # Apply U_f to bit n+1 -> 1, bit 0 is the helper bit
        p.inst(tuple(["U_f"] + self.__qubits))

        # Apply final H to the rest of bits
        for n_ in range(1, self.__num_qubits+1):
            p.inst(H(n_))

        self.__circuit = p

    def run(self, trials, isQC = False):
        sum_bits = 0
        if isQC:
            qc = get_qc(f"{self.__num_qubits+1}q-qvm")
            qc.compiler.client.timeout = 1000
            results = qc.run_and_measure(self.__circuit, trials=trials)
            del results[0]
            for _, v in results.items():
                sum_bits += sum(v)
        else:
            # Final measurement
            self.__classic_regs = list(range(self.__num_qubits))
            for i, n_ in enumerate(list(range(1, self.__num_qubits+1))[::-1]):
                self.__circuit.measure(n_, self.__classic_regs[i])
            qvm = api.QVMConnection()
            results = qvm.run(self.__circuit)
            sum_bits = sum([s for sub in results for s in sub])
        if not sum_bits:
            return 1 # return 1 for constant
        else:
            return 0 # return 0 for balanced
