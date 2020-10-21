from Configuration import Configuration
import pandas as pd
import numpy as np
from qiskit import (
    IBMQ,
    QuantumCircuit,
    execute,
    Aer
)
from qiskit.tools.monitor import job_monitor
from qiskit.visualization import plot_histogram
from timeit import default_timer as timer
from itertools import permutations
import logging
from logging.config import fileConfig

# Setup logging
fileConfig('Configuration/logging_config.ini')
logger = logging.getLogger()

# Setup config parser and determine whether to run on live hardware
config = Configuration.NY167Config()
run_on_live_hardware = config.get_boolean('app', 'run_on_live_hardware')

# Set number of qubits and classical bits
num_qbits = 4
num_cbits = 4
num_shots = 5000


def build_test_circuit() -> QuantumCircuit:
    # Create a Quantum Circuit acting on the q register
    circuit = QuantumCircuit(num_qbits, num_cbits)

    # Add a H gate on qubit 0
    circuit.h([0, 2])

    # Add a CX (CNOT) gate on control qubit 0 and target qubit 1
    circuit.cx([0, 2], [1, 3])

    circuit.mcx([0, 1, 2], 3)

    # Map the quantum measurement to the classical bits
    circuit.measure([0, 1, 2, 3], [0, 1, 2, 3])

    return circuit


def run_test():
    circuit = build_test_circuit()
    print(circuit.draw())

    start_time = timer()

    if run_on_live_hardware:
        # Load the account to get actual hardware information
        IBMQ.load_account()

        # For using IBM-Q computers
        provider = IBMQ.get_provider('ibm-q')
        qcomp = provider.get_backend('ibmq_16_melbourne')

        # Execute the circuit on the live hardware
        job = execute(experiments=circuit, backend=qcomp, shots=num_shots)

        job_monitor(job=job)
    else:
        # Use Aer's qasm_simulator
        simulator = Aer.get_backend('qasm_simulator')

        # Execute the circuit on the qasm simulator
        job = execute(experiments=circuit, backend=simulator, shots=num_shots)

    # Grab results from the job
    result = job.result()

    # Calculate total compute time taken
    end_time = timer()

    logger.debug(f"Total compute/queue time: {end_time - start_time:.2f}s")

    # Returns counts
    counts = result.get_counts(circuit)

    # Get algorithm time taken
    try:
        print(result)
        for result in result.results:
            logger.debug(f"Algorithm time taken: {result.time_taken}s")
    except Exception as ex:
        logger.debug(ex)

    return counts


if __name__ == '__main__':
    IBMQ.save_account(config.get('api', 'api-token'))

    num_tests = 1
    test_values = [{k: v for k, v in run_test().items()} for y in range(num_tests)]

    df = pd.DataFrame(test_values)

    print(df.head())

    qbit_permutations = set([''.join(p[:num_qbits]) for p in permutations(['0', '1']*num_qbits)])

    expected_values = ['0000', '0011', '0111', '1100']
    total_expected = 0

    for qbit_p in sorted(qbit_permutations):
        average_qbit_p = df.get(qbit_p, np.zeros(1)).sum() / num_tests
        if qbit_p in expected_values:
            total_expected += average_qbit_p
        logger.debug(f"Average {qbit_p}: {average_qbit_p}")
    logger.debug(f"Error rate:   {1 - (total_expected / num_shots)}")
