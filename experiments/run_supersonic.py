"""
Experiment runner for Supersonic OT benchmarks
"""

from protocols.supersonic_ot import (
    SupersonicParams, SupersonicOTSender, SupersonicOTReceiver, Dealer
)
from framework.benchmark import BenchmarkTimer, MemoryTracker, BandwidthTracker
from framework.communication import ChannelPair
from framework.metrics import MetricsCollector, TrialResult


# Run one complete Supersonic OT exchange and measure everything
def run_single_trial(params: SupersonicParams, m0: bytes, m1: bytes,
    choice_bit: int, trial_number: int) -> TrialResult:

    bw = BandwidthTracker()
    pair = ChannelPair(bandwidth_tracker=bw)

    # Dealer pre-processing
    dealer = Dealer(params)
    sender_shares, receiver_shares = dealer.generate_shares()

    receiver = SupersonicOTReceiver(params)
    sender = SupersonicOTSender(params)

    with MemoryTracker() as mem:
        with BenchmarkTimer() as total:

            # Step 1: Receiver masks choice
            with BenchmarkTimer() as receiver_timer:
                e = receiver.mask_choice(choice_bit, receiver_shares)

            pair.receiver.send(e, label="masked_choice")

            # Step 2: Sender receives masked choice and encrpts
            recv_e = pair.sender.receive(label="masked_choice")

            with BenchmarkTimer() as sender_timer:
                ciphertext = sender.encrypt(sender_shares, recv_e, m0, m1)

            pair.sender.send(ciphertext, label="ciphertext")

            # Step 3: Sender receives keys and encrypts
            recv_ct = pair.receiver.receive(label="ciphertext")

            with BenchmarkTimer() as receiver_decrypt_timer:
                recovered = receiver.decrypt(recv_ct)


    expected = m0 if choice_bit == 0 else m1
    correct = (recovered == expected)

    return TrialResult(
        protocol_name="supersonic_ot",
        trial_number=trial_number,
        message_bits=len(m0) * 8,
        execution_time_ms=total.elapsed_ms,
        sender_time_ms=sender_timer.elapsed_ms,
        receiver_time_ms=receiver_timer.elapsed_ms + receiver_decrypt_timer.elapsed_ms,
        peak_memory_kb=mem.peak_kb,
        bytes_sent=bw.bytes_sent,
        bytes_received=bw.bytes_received,
        message_count=bw.message_count,
        correct=correct,
    )

# Run the full Supersonic OT experiment across parameter sizes
def run_experiment(num_trials: int = 20, warmup_trials: int = 5):

    param_sets = {
        "small": SupersonicParams.small(),
        "medium": SupersonicParams.medium(),
        "large": SupersonicParams.large(),
    }

    for label, params in param_sets.items():
        collector = MetricsCollector(f"supersonic_ot_{label}")

        msg_size = params.message_bytes
        m0 = bytes(range(msg_size)) * (msg_size // 256 + 1)
        m0 = m0[:msg_size]
        m1 = bytes(range(255, 255 - msg_size, -1)) * (msg_size // 256 + 1)
        m1 = m1[:msg_size]

        # Warm-up
        print(f"  Warming up {label} ({warmup_trials} trials)...")

        # Measured trials
        print(f" Running {num_trials} measured trials...")
        for i in range(num_trials):
            choice = i % 2
            result = run_single_trial(params, m0, m1, choice, i)
            collector.add_result(result)

        collector.print_summary()
        collector.export_csv(f"results/logs/supersonic_ot_{label}.csv")

if __name__ == "__main__":
    run_experiment()
