from pyquil import get_qc, Program
from pyquil.gates import CNOT, Z, H
from pyquil.api import local_forest_runtime
# construct a Bell State program
p = Program(H(0), CNOT(0, 1))
# run the program on a QVM
with local_forest_runtime():
    qc = get_qc('9q-square-qvm')
    result = qc.run_and_measure(p, trials=10)
    print(result[0])
    print(result[1])