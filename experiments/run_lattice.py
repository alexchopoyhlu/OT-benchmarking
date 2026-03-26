"""
Experiment runner for Lattice OT benchmarks.

Runs the Mod-LWR OT protocol for multiple trials across
different parameter sizes and collects performance metrics.
"""

import threading

from protocols.lattice_ot import LatticeOTSender, LatticeOTReceiver, LatticeParams
from framework.benchmark import BenchmarkTimer, MemoryTracker, BandwidthTracker
from framework.communication import ChannelPair
from framework.metrics import MetricsCollector, TrialResult

# Run one complete OT protocol exchange and measure everything
def run_single_trial(params: LatticeParams, m0: bytes, m1: bytes, choice_bit: int, trial_number: int) -> TrialResult:

    bw = BandwidthTracker()
    pair = ChannelPair(bandwidth_tracker=bw)

    # Store results from each thread
    sender_time = {}
    receiver_time = {}
    result_holder = {}

    def sender_side():
        sender = LatticeOTSender(params)

        # Receive public matrix from receiver
        public_matrix = pair.sender.receive(label="public_matrix")

        # Receive public keys from receiver
        receiver_pk = pair.sender.receive(label="receiver_pk")

        # Encrypt and send ciphertexts
        with BenchmarkTimer() as t:
            ciphertext = sender.encrypt(public_matrix, receiver_pk, m0, m1)
        sender_time["ms"] = t.elapsed_ms

        pair.sender.send(ciphertext, label="ciphertext")

    def receiver_side():
        receiver = LatticeOTReceiver(params)

        # Setup and send public matrix
        with BenchmarkTimer() as t:
            public_matrix = receiver.setup()
            pair.receiver.send(public_matrix, label="public_matrix")

            # Generate keys and send to sender
            receiver_pk = receiver.generate_keys(choice_bit, public_matrix)
            pair.receiver.send(receiver_pk, label="receiver_pk")

            # Receive ciphertexts and decrypt
            ciphertext = pair.receiver.receive(label="ciphertext")
            recovered = receiver.decrypt(ciphertext, len(m0) if choice_bit == 0 else len(m1))
        receiver_time["ms"] = t.elapsed_ms

        expected = m0 if choice_bit == 0 else m1
        result_holder["correct"] = (recovered == expected)
        result_holder["incorrect"] = recovered

    # Run with overall timing/memory tracking
    with MemoryTracker() as mem:
        with BenchmarkTimer() as total:
            t1 = threading.Thread(target=sender_side)
            t2 = threading.Thread(target=receiver_side)
            t1.start()
            t2.start()
            t1.join()
            t2.join()

    return TrialResult(
        protocol_name="lattice_ot",
        trial_number=trial_number,
        message_bits=len(m0) * 8,
        execution_time_ms=total.elapsed_ms,
        sender_time_ms=sender_time.get("ms", 0),
        receiver_time_ms=receiver_time.get("ms", 0),
        peak_memory_kb=mem.peak_kb,
        bytes_sent=bw.bytes_sent,
        bytes_received=bw.bytes_received,
        message_count=bw.message_count,
        correct=result_holder.get("correct", False),
    )


# Run the full lattice OT experiment across parameter sizes
def run_experiment(num_trials: int = 20):

    param_sets = {
        "small": LatticeParams.small(),
        "medium": LatticeParams.medium(),
        "large": LatticeParams.large(),
    }

    for label, params in param_sets.items():
        collector = MetricsCollector(f"lattice_ot_{label}")

        # Generate test message of the right size
        msg_size = params.message_bits // 8
        m0 = bytes(range(msg_size)) * (msg_size // 256 + 1)
        m0 = m0[:msg_size]
        m1 = bytes(range(255, 255 - msg_size, -1)) * (msg_size // 256 + 1)
        m1 = m1[:msg_size]

        for i in range(num_trials):
            choice = i % 2 # Alternate between 0 and 1
            result = run_single_trial(params, m0, m1, choice, i)
            collector.add_result(result)

        collector.print_summary()
        collector.export_csv(f"results/logs/lattice_ot_{label}.csv")

if __name__ == "__main__":
    run_experiment()
