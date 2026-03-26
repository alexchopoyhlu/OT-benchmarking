"""
Side-by-side comparison of Lattice OT and Supersonic OT

Runs both protocols under identical conditions and produces
a combined results file for Chapter 5 analysis.
"""
from random import choice
import time

from experiments.run_lattice import run_single_trial as run_lattice_trial
from experiments.run_supersonic import run_single_trial as run_supersonic_trial
from protocols.lattice_ot import LatticeParams
from protocols.supersonic_ot import SupersonicParams
from framework.metrics import MetricsCollector
from framework.communication import ChannelPair, create_socket_pair


# Run both protocols at comparable message sizes
def run_comparison(num_trials: int = 20, warmup_trials: int = 5, use_sockets: bool = False):
    start_time = time.time()

    # Define matching parameter pairs
    comparisons = [
        {
            "label": "small",
            "lattice_params": LatticeParams.small(),
            "supersonic_params": SupersonicParams.small(),
        },
        {
            "label": "medium",
            "lattice_params": LatticeParams.medium(),
            "supersonic_params": SupersonicParams.medium(),
        },
        {
            "label": "large",
            "lattice_params": LatticeParams.large(),
            "supersonic_params": SupersonicParams.large(),
        },
    ]

    for comp in comparisons:
        label = comp["label"]
        l_params = comp["lattice_params"]
        s_params = comp["supersonic_params"]

        print(f"\n>>> Running comparison: {label} <<<\n")

        # Generate messages of matching size and use smaller of two for fair comparison
        msg_size = min(l_params.message_bits // 8, s_params.message_bytes)
        m0 = bytes(range(msg_size)) * (msg_size // 256 + 1)
        m0 = m0[:msg_size]
        m1 = bytes(range(255, 255 - msg_size, -1)) * (msg_size // 256 + 1)
        m1 = m1[:msg_size]

        # Warmup trials
        print(f"  Warming up ({warmup_trials} trials)...")
        for i in range(warmup_trials):
            run_lattice_trial(l_params, m0, m1, i % 2, i)
            run_supersonic_trial(s_params, m0, m1, i % 2, i)

        # Actual measurement
        print(f"  Running {num_trials} measured trials...")
        lattice_collector = MetricsCollector(f"comparison_lattice_{label}")
        for i in range(num_trials):
            choice = i % 2
            result = run_lattice_trial(l_params, m0, m1, choice, i)
            lattice_collector.add_result(result)

        supersonic_collector = MetricsCollector(f"comparison_supersonic_{label}")
        for i in range(num_trials):
            choice = i % 2
            result = run_supersonic_trial(s_params, m0, m1, choice, i)
            supersonic_collector.add_result(result)


        # Print summaries
        print("--- Lattice OT ---")
        lattice_collector.print_summary()
        print("--- Supersonic OT ---")
        supersonic_collector.print_summary()

        # Export
        lattice_collector.export_csv(f"results/logs/comparison_lattice_{label}.csv")
        supersonic_collector.export_csv(f"results/logs/comparison_supersonic_{label}.csv")

        total_time = time.time() - start_time
        print(f"\n>>> Total comparison runtime: {total_time:.2f} seconds <<<\n")


if __name__ == "__main__":
    import sys
    use_sockets = "--sockets" in sys.argv
    if use_sockets:
        print("Running with TCP socket communication\n")
    else:
        print("Running with in-process communication\n")
    run_comparison(use_sockets=use_sockets)
