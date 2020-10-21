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

run_on_live_hardware = True


def build_test_circuit() -> QuantumCircuit:
    # Create a Quantum Circuit acting on the q register
    circuit = QuantumCircuit(2, 2)

    # Add a H gate on qubit 0
    circuit.h(0)

    # Add a CX (CNOT) gate on control qubit 0 and target qubit 1
    circuit.cx(0, 1)

    # Map the quantum measurement to the classical bits
    circuit.measure([0, 1], [0, 1])

    return circuit


def run_test():
    circuit = build_test_circuit()

    start_time = timer()

    if run_on_live_hardware:
        # Load the account to get actual hardware information
        IBMQ.load_account()

        # For using IBM-Q computers
        provider = IBMQ.get_provider('ibm-q')
        qcomp = provider.get_backend('ibmq_16_melbourne')

        # Execute the circuit on the live hardware
        job = execute(experiments=circuit, backend=qcomp, shots=1000)

        job_monitor(job=job)
    else:
        # Use Aer's qasm_simulator
        simulator = Aer.get_backend('qasm_simulator')

        # Execute the circuit on the qasm simulator
        job = execute(experiments=circuit, backend=simulator, shots=1000)

    # Grab results from the job
    result = job.result()

    # Calculate total compute time taken
    end_time = timer()

    print(f"Total compute/queue time: {end_time - start_time:.2f}s")

    # Returns counts
    counts = result.get_counts(circuit)
    # print("\nTotal count for 00 and 11 are:", counts)

    # Draw the circuit
    circuit.draw()

    return counts


if __name__ == '__main__':
    config = Configuration.NY167Config()
    IBMQ.save_account(config.get('api', 'api-token'))

    num_tests = 1
    test_values = [{k: v for k, v in run_test().items()} for y in range(num_tests)]

    df = pd.DataFrame(test_values)

    print(df.head())

    average_00 = df['00'].sum() / num_tests
    average_11 = df['11'].sum() / num_tests

    print(f"Average 00: {average_00}")
    print(f"Average 11: {average_11}")

    if run_on_live_hardware:
        average_01 = df['01'].sum() / num_tests
        average_10 = df['10'].sum() / num_tests

        print(f"Average 01: {average_01}")
        print(f"Average 10: {average_10}")
