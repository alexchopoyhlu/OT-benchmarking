"""
Experiment runner for Supersonic OT benchmarks
"""

import threading

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

    sender_time = {}
    receiver_time = {}
    result_holder = {}

    # Dealer pre-processing (measured separately)
    with BenchmarkTimer() as dealer_timer:
        dealer = Dealer(params)
        sender_shares, receiver_shares = dealer.generate_shares()

    def sender_side():
        sender = SupersonicOTSender(params)

        # Receive masked choice bit from receiver
        e = pair.sender.receive(label="masked_choice")

        # Encrypt and send ciphertexts
        with BenchmarkTimer() as t:
            ciphertext = sender.encrypt(sender_shares, e, m0, m1)
        sender_time["ms"] = t.elapsed_ms

        pair.sender.send(ciphertext, label="ciphertext")


    def receiver_side():
        receiver = SupersonicOTReceiver(params)

        with BenchmarkTimer() as t:
            # Mask choice and send to sender
            e = receiver.mask_choice(choice_bit, receiver_shares)
            pair.receiver.send(e, label="masked_choice")

            # Receive ciphertexts and decrypt
            ciphertext = pair.receiver.receive(label="ciphertext")
            recovered = receiver.decrypt(ciphertext)
        receiver_time["ms"] = t.elapsed_ms

        expected = m0 if choice_bit == 0 else m1
        result_holder["correct"] = (recovered == expected)


    # Run with overall timing and memory tracking
    with MemoryTracker() as mem:
        with BenchmarkTimer() as total:
            t1 = threading.Thread(target=sender_side)
            t2 = threading.Thread(target=receiver_side)
            t1.start()
            t2.start()
            t1.join()
            t2.join()

    return TrialResult(
        protocol_name="supersonic_ot",
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

# Run the full Supersonic OT experiment across parameter sizes
def run_experiment(num_trials: int = 20):

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

        for i in range(num_trials):
            choice = i % 2
            result = run_single_trial(params, m0, m1, choice, i)
            collector.add_result(result)

        collector.print_summary()
        collector.export_csv(f"results/logs/supersonic_ot_{label}.csv")

if __name__ == "__main__":
    run_experiment()
