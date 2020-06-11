import numpy as np
import math, time, sys

from qiskit import QuantumCircuit, execute, assemble, transpile, IBMQ
from qiskit.quantum_info.operators import Operator
from qiskit.circuit.library.standard_gates import ZGate


'''

---------- GROVER'S ALGORITHM SOLVER ---------

This Python class implements a Grover's algorithm solver. The GroverSolver
object is instantiated with two parameters:

    num_qubits : the number of qubits that the circuit needs to have

    f : a reference to the function which maps inputs to 0 if they are "bad"
        values and maps inputs to 1 if they are "awesome" values

The GroverSolver class then builds a circuit that is capable of finding the
input which the function f maps to 1. This is accomplished in 3 steps.

    1. The private method __instantiate_qubits is called. This method creates
       the qubits that later functions will use.

    2. The private method __compute_matrices is called. This method creates the
       three custom matrices that will be needed in the quantum circuit. The
       first is the Z_f matrix. This matrix will flip the amplitude for the
       answer vector. The second matrix is the Z_0 matrix. This matrix
       will flip the amplitude for the 0^n vector. The last matrix is the
       "ne-gate" matrix. This matrix flips the amplitude for every vector.

    3. The private method __build_grover_circuit is called. This method
       compiles all the necessary quantum gates to make a circuit that
       implements Grover's algorithm. This circuit contains Hadamard gates as
       well as the gates defined in step 2.

Once the object is initialized, the users can simply call the method to run the
circuit. This method has one parameters and a return value:

    trials : the number of times to execute the circuit

    return : the result of the trials formatted as a dictionary where each
             qubit index maps to an array which contains the measurement of
             that qubit for each trial

'''


'''
##########################################################################
#                                                                        #
#                   GROVER'S ALGORITHM IMPLEMENTATION                    #
#                                                                        #
##########################################################################
'''


class GroverSolver(object):

    def __init__(self, num_qubits, f):
        self.__num_qubits = num_qubits
        self.__f = f
        self.__compute_matrices()
        self.__build_grover_circuit()


    def __compute_matrices(self):
        # build Zf matrix based on function f
        for i in range(2**self.__num_qubits):
            if self.__f(format(i, '0' + str(self.__num_qubits) + 'b')) == 1:
                self.__zf = format(i, '0' + str(self.__num_qubits) + 'b')[::-1]
                break


    def __num_iterations(self):
        return math.floor((math.pi / 4) * math.sqrt(2**self.__num_qubits))


    def __build_grover_circuit(self):
        # initialize program and define new gates
        p = QuantumCircuit(self.__num_qubits, self.__num_qubits)
        zf = ZGate().control(self.__num_qubits - 1)
        z0 = ZGate().control(self.__num_qubits - 1)

        # apply first round of Hadamard gates
        for i in range(self.__num_qubits):
            p.h(i)

        # apply Grover as many times as needed
        for i in range(self.__num_iterations()):
            for index, i in enumerate(self.__zf):
                if i == '0':
                    p.x(index)

            p.append(zf, list(range(self.__num_qubits)))

            for index, i in enumerate(self.__zf):
                if i == '0':
                    p.x(index)

            for i in range(self.__num_qubits):
                p.h(i)

            for i in range(self.__num_qubits):
                p.x(i)

            p.append(z0, list(range(self.__num_qubits)))

            for i in range(self.__num_qubits):
                p.x(i)

            for i in range(self.__num_qubits):
                p.h(i)

        # measure the qubits
        p.measure(list(range(self.__num_qubits)), list(range(self.__num_qubits)))

        # save the grover circuit
        self.__grover_circuit = p


    def run(self, trials):
        backend = provider.backends.ibmq_burlington
        #backend = provider.backends.ibmq_qasm_simulator
        job = execute(self.__grover_circuit, backend=backend, shots=trials, optimization_level=3)
        result = job.result()
        circuit = self.__grover_circuit.draw()
        time_taken = result.time_taken
        counts = result.get_counts()
        return circuit, time_taken, counts


'''
##########################################################################
#                                                                        #
#                 CODE FOR RUNNING GROVER'S ALGORITHM                    #
#                                                                        #
##########################################################################
'''

provider = IBMQ.load_account()

f = lambda x : int(x == '001')
grover_solver = GroverSolver(3, f)
circuit, time_taken, counts = grover_solver.run(1000)
print(circuit)
print("Time Taken to Execute Circuit with 3 Qubits: " + str(time_taken))
print(counts)
