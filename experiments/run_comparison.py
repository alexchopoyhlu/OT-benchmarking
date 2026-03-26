"""
Side-by-side comparison of Lattice OT and Supersonic OT

Runs both protocols under identical conditions and produces
a combined results file for Chapter 5 analysis.
"""

from experiments.run_lattice import run_single_trial as run_lattice_trial
from experiments.run_supersonic import run_single_trial as run_supersonic_trial
from protocols.lattice_ot import LatticeParams
from protocols.supersonic_ot import SupersonicParams
from framework.metrics import MetricsCollector


# Run both protocols at comparable message sizes
def run_comparison(num_trials: int = 30):

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

        # Run lattice OT
        lattice_collector = MetricsCollector(f"comparison_lattice_{label}")
        for i in range(num_trials):
            choice = i % 2
            result = run_lattice_trial(l_params, m0, m1, choice, i)
            lattice_collector.add_result(result)

        # Run supersonic OT
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

if __name__ == "__main__":
    run_comparison()
