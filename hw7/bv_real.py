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
import random

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
        #print(p.draw())
        #print(p.draw(output="latex_source"))
        self.__circuit = p

    def run(self, trials):
        print(f"Both repeated for {trials} times")
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
        print(f"real device: function = {real_most_common} * x + {self.__b}")
        #------ Simulator
        simulator = Aer.get_backend("qasm_simulator")
        start_time = time.time()
        job = execute(self.__circuit, simulator, shots=trials)
        print("--- Simulator takes %s seconds ---" % (time.time() - start_time))
        sim_result = job.result().get_counts()
        print('simulator result count:')
        print(sim_result)
        sim_most_common = [k for k, v in sorted(sim_result.items(), key=lambda item: item[1])][-1]
        print(f"simulator: function = {sim_most_common} * x + {self.__b}")
        return sim_most_common, self.__b

# ------------------------- Test case -------------------------
"""
n = 4
a_str = '1101'
b_str = '1'
print(f"Number of Q bits is {n}")
print(f"expected: function = {a_str} * x + {b_str}")

def f(x, a_str, b_str, nbits):
    a = int(a_str, 2)
    b = int(b_str, 2)
    ax = format((x & a), '0'+str(nbits)+'b').count('1') % 2
    return (ax + b) % 2

def f_1(x):
    return f(x, a_str, b_str, n)

# Initialize the DJ solver and run with 1000 trials
a, b = BernsteinVaziraniSolver(n,f_1).run(8192)
# Calculate the execution time
print(f"function = {a} * x + {b}")
"""
# ------------------------ Evaluation ------------------------

class BernsteinVaziraniEvaluator(object): 
    # Constructor
    def __init__(self, num_qubits):
        self.__num_qubits = num_qubits
        self.__num_scenario = 2 ** self.__num_qubits
        # Gate Counts
        self.__num_h_gate = 0
        self.__num_x_gate = 0
        self.__num_i_gate = 0
        self.__num_cnot_gate = 0
        self.__num_total_gate = 0
        
    
    def __build_circuit(self, a_scenario_idx = 0):
        p = QuantumCircuit(self.__num_qubits+1, self.__num_qubits)
        self.__num_h_gate = 0
        self.__num_x_gate = 0
        self.__num_i_gate = 0
        self.__num_cnot_gate = 0
        
        # Apply H Gates to the first N qubits
        for q_idx in range(self.__num_qubits):
            p.h(q_idx)
            self.__num_h_gate += 1
            
        # Set the last qubit to |->
        p.x(self.__num_qubits); self.__num_x_gate += 1
        p.h(self.__num_qubits); self.__num_h_gate += 1
        
        # Get the A String for Oracle
        a_str = format(a_scenario_idx, f'0{self.__num_qubits}b')
    
        # Apply the inner-product oracle
        a_str = a_str[::-1] # reverse a to fit qiskit's qubit ordering
        for q_idx in range(self.__num_qubits):
            if a_str[q_idx] == '0':
                p.i(q_idx); self.__num_i_gate += 1
            else:
                p.cx(q_idx, self.__num_qubits); self.__num_cnot_gate += 1

        # Apply H gate again to the first N qubits
        for q_idx in range(self.__num_qubits):
            p.h(q_idx)
            self.__num_h_gate += 1
        
        # Count the number of total gate
        self.__num_total_gate = self.__num_h_gate + self.__num_cnot_gate + self.__num_x_gate + self.__num_i_gate
        
        # measure the qubits
        p.measure(range(self.__num_qubits), range(self.__num_qubits))

        # Finish creating the Circuit
        self.__circuit = p

    def run(self, trials):
        #------ Real
        provider = IBMQ.get_provider(hub='ibm-q')
        backend = least_busy(provider.backends(filters=lambda x: x.configuration().n_qubits >= (self.__num_qubits+1) and
                                   not x.configuration().simulator and x.status().operational==True))
        #print("Now using least busy backend: ", backend)
        job = execute(self.__circuit, backend=backend, shots=trials, optimization_level=3)
        #job_monitor(job, interval = 2)
        real_results = job.result()
        #print("--- Real Quantum Computer takes %s seconds ---" % (real_results.time_taken))
        real_time = real_results.time_taken
        real_result = real_results.get_counts()
        real_most_common = [k for k, v in sorted(real_result.items(), key=lambda item: item[1])][-1]
        """
        print('real result count:')
        print(real_result)
        if int(real_most_common) == 0:
            print(f"Real: Function is Constant Function")
        else:
            print(f"Real: Function is Balanced Function")
        """
        #------ Simulator
        simulator = Aer.get_backend("qasm_simulator")
        start_time = time.time()
        job = execute(self.__circuit, simulator, shots=trials)
        sim_time = time.time() - start_time
        #print("--- Simulator takes %s seconds ---" % (sim_time))
        sim_result = job.result().get_counts()
        #print('simulator result count:')
        #print(sim_result)
        sim_most_common = [k for k, v in sorted(sim_result.items(), key=lambda item: item[1])][-1]
        return real_time, sim_time, real_most_common, sim_most_common, backend


    def eval(self, trials):
        a_list = list(range(0, self.__num_scenario));random.shuffle(a_list); a_list = a_list[0:min(10, self.__num_scenario)]
        for a_scenario_idx in a_list:
            a_str = format(a_scenario_idx, f'0{self.__num_qubits}b')
            self.__build_circuit(a_scenario_idx=a_scenario_idx)
            real_time, sim_time, real_most_common, sim_most_common, backend = self.run(trials)
            print(f'{self.__num_qubits}, {self.__num_x_gate}, {self.__num_h_gate}, {self.__num_i_gate}, {self.__num_cnot_gate}, {self.__num_total_gate}, {real_time}, {sim_time}, {a_str}, {real_most_common}, {sim_most_common}, {backend}, {trials}')

IBMQ.load_account()
print('num_qubits, num_x_gate, num_h_gate, num_i_gate, num_cnot_gate, num_total_gate, real_time, sim_time, answer, real_result, sim_result, backand_name, trials')
for num_qubit in reversed(range(1, 15)):
    bv_eval = BernsteinVaziraniEvaluator(num_qubit)
    trials = min(8192, 2 ** (num_qubit + 3))
    trials = max(1024, trials)
    bv_eval.eval(trials)