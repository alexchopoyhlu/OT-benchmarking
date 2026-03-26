"""
Experiment runner for Lattice OT benchmarks.

Runs the Mod-LWR OT protocol for multiple trials across
different parameter sizes and collects performance metrics.
"""

from protocols.lattice_ot import LatticeOTSender, LatticeOTReceiver, LatticeParams
from framework.benchmark import BenchmarkTimer, MemoryTracker, BandwidthTracker
from framework.communication import ChannelPair
from framework.metrics import MetricsCollector, TrialResult

# Run one complete OT protocol exchange and measure everything
def run_single_trial(params: LatticeParams, m0: bytes, m1: bytes, choice_bit: int, trial_number: int) -> TrialResult:

    bw = BandwidthTracker()
    pair = ChannelPair(bandwidth_tracker=bw)

    receiver = LatticeOTReceiver(params)
    sender = LatticeOTSender(params)

    with MemoryTracker() as mem:
        with BenchmarkTimer() as total:

            # Step 1: Receiver setup
            public_matrix = receiver.setup()
            pair.receiver.send(public_matrix, label="public_matrix")

            # Step 2: Receiver generates keys
            receiver_pk = receiver.generate_keys(choice_bit, public_matrix)
            pair.receiver.send(receiver_pk, label="receiver_pk")

            # Step 3: Sender receives keys and encrypts
            recv_matrix = pair.sender.receive(label="public_matrix")
            recv_pk = pair.sender.receive(label="receiver_pk")

            with BenchmarkTimer() as sender_timer:
                ciphertext = sender.encrypt(recv_matrix, recv_pk, m0, m1)

            pair.sender.send(ciphertext, label="ciphertext")

            # Step 4: Receiver decrypts
            recv_ct = pair.receiver.receive(label="ciphertext")

            with BenchmarkTimer() as receiver_timer:
                expected_len = len(m0) if choice_bit == 0 else len(m1)
                recovered = receiver.decrypt(recv_ct, expected_len)

    expected = m0 if choice_bit == 0 else m1
    correct = (recovered == expected)

    return TrialResult(
        protocol_name="lattice_ot",
        trial_number=trial_number,
        message_bits=len(m0) * 8,
        execution_time_ms=total.elapsed_ms,
        sender_time_ms=sender_timer.elapsed_ms,
        receiver_time_ms=receiver_timer.elapsed_ms,
        peak_memory_kb=mem.peak_kb,
        bytes_sent=bw.bytes_sent,
        bytes_received=bw.bytes_received,
        message_count=bw.message_count,
        correct=correct,
    )


# Run the full lattice OT experiment across parameter sizes
def run_experiment(num_trials: int = 20, warmup_trials: int = 5):

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

        # Warm-up
        print(f"  Warming up {label} ({warmup_trials} trials)...")
        for i in range(warmup_trials):
            run_single_trial(params, m0, m1, i % 2, i)

        # Measured trials
        print(f"  Running {num_trials} measured trials...")
        for i in range(num_trials):
            choice = i % 2 # Alternate between 0 and 1
            result = run_single_trial(params, m0, m1, choice, i)
            collector.add_result(result)

        collector.print_summary()
        collector.export_csv(f"results/logs/lattice_ot_{label}.csv")

if __name__ == "__main__":
    run_experiment()
