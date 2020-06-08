# importing necessary package
import numpy as np
import math
from qiskit import QuantumCircuit, execute, Aer
from qiskit.quantum_info.operators import Operator
from qiskit import IBMQ, BasicAer
from qiskit.providers.ibmq import least_busy
from qiskit.visualization import plot_histogram
from qiskit.tools.monitor import job_monitor
import time

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
        #------ Real
        IBMQ.save_account('1388dc1e10847ac5041cf9fcad4cf44f8390163c0840e3dc5a1733622d3a3c413893a61e7d12b31611d810bf2aa318bc713dc929d4ef1f61954021f1346a8934',overwrite=True)
        IBMQ.load_account()
        provider = IBMQ.get_provider(hub='ibm-q')
        backend = least_busy(provider.backends(filters=lambda x: x.configuration().n_qubits >= (n+1) and
                                   not x.configuration().simulator and x.status().operational==True))
        print("Now using least busy backend: ", backend)
        job = execute(self.__circuit, backend=backend, shots=trials, optimization_level=3)
        job_monitor(job, interval = 2)
        real_results = job.result()
        print("--- Real Quantum Computer takes %s seconds ---" % (real_results.time_taken))
        real_result = real_results.get_counts()
        real_most_common = [k for k, v in sorted(real_result.items(), key=lambda item: item[1])][-1]
        print('real result count:')
        print(real_result)
        if int(real_most_common) == 0:
            print(f"Real: Function is Constant Function")
        else:
            print(f"Real: Function is Balanced Function")
        #------ Simulator
        simulator = Aer.get_backend("qasm_simulator")
        start_time = time.time()
        job = execute(self.__circuit, simulator, shots=trials)
        print("--- Simulator takes %s seconds ---" % (time.time() - start_time))
        sim_result = job.result().get_counts()
        print('simulator result count:')
        print(sim_result)
        sim_most_common = [k for k, v in sorted(sim_result.items(), key=lambda item: item[1])][-1]
        if int(sim_most_common) == 0:
            print(f"Simulator: Function is Constant Function")
            return False # Const
        else:
            print(f"Simulator: Function is Balanced Function")
            return True # Balanced

# ------------------------- Test case -------------------------

n = 3

def f_balanced(x):
    if x >= 2**(n-1):
        return 1
    else:
        return 0

def f_const(x):
    return 1

print(f"Number of Q bits is {n}")

# Initialize the DJ solver and run with 1000 trials
dj_solver = DeutschJozsaSolver(n, f_balanced)
result = ""
if dj_solver.run(1000):
    result = "Balanced"
else:
    result = "Const"
print(f"Function is {result}")