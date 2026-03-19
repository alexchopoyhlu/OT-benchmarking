"""
Metrics collection and experiment logging

Collects benchmark measurements from protocol runs and exports to CSV
for analysis. This generates the data for Chapter 5.
"""

import csv
import json
import os
import statistics
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# Results from a single protocol execution trial
@dataclass
class TrialResult:
    protocol_name: str
    trial_number: int
    message_bits: int
    execution_time_ms: float
    sender_time_ms: float = 0.0
    receiver_time_ms: float = 0.0
    peak_memory_kb: float = 0.0
    bytes_sent: int = 0
    bytes_received: int = 0
    message_count: int = 0
    correct: bool = True


# Collects trial results and exports to CSV/JSON
class MetricsCollector:
    def __init__(self, experiment_name: str):
        self.experiment_name = experiment_name
        self.results: list[TrialResult] = []
        self.start_time = datetime.now()

    def add_result(self, result: TrialResult):
        self.results.append(result)

    def export_csv(self, filepath: str) -> None:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        fieldnames = [
            "protocol_name", "trial_number", "message_bits", "execution_time_ms", "sender_time_ms", "receiver_time_ms", "peak_memory_kb", "bytes_sent", "bytes_received", "message_count", "correct"
        ]

        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in self.results:
                writer.writerow({
                    "protocol_name": r.protocol_name,
                    "trial_number": r.trial_number,
                    "message_bits": r.message_bits,
                    "execution_time_ms": r.execution_time_ms,
                    "sender_time_ms": r.sender_time_ms,
                    "receiver_time_ms": r.receiver_time_ms,
                    "peak_memory_kb": r.peak_memory_kb,
                    "bytes_sent": r.bytes_sent,
                    "bytes_received": r.bytes_received,
                    "message_count": r.message_count,
                    "correct": r.correct
                })

        print(f"Results exported to {filepath}")

    def export_json(self, filepath: str) -> None:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        data = {
            "experiment": self.experiment_name,
            "timestamp": self.start_time.isoformat(),
            "num_trials": len(self.results),
            "results": [
                {
                    "protocol_name": r.protocol_name,
                    "trial_number": r.trial_number,
                    "message_bits": r.message_bits,
                    "execution_time_ms": round(r.execution_time_ms, 4),
                    "peak_memory_kb": round(r.peak_memory_kb, 2),
                    "bytes_sent": r.bytes_sent,
                    "bytes_received": r.bytes_received,
                    "correct": r.correct
                }
                for r in self.results
            ],
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        print(f"Results exported to {filepath}")

    def print_summary(self) -> None:
        if not self.results:
            print("No results collected.")
            return

        times = [r.execution_time_ms for r in self.results]
        memories = [r.peak_memory_kb for r in self.results]
        bandwidths = [r.bytes_sent + r.bytes_received for r in self.results]
        correct_count = sum(1 for r in self.results if r.correct)

        print(f"\n{'=' * 60}")
        print(f"  Experiment: {self.experiment_name}")
        print(f"  Protocol: {self.results[0].protocol_name}")
        print(f"  Trials: {len(self.results)}")
        print(f"  Correct: {correct_count}/{len(self.results)}")
        print(f"{'=' * 60}")
        print(f"  Execution time(ms):")
        print(f"    Mean:   {sum(times) / len(times):.3f}")
        print(f"    Min:    {min(times):.3f}")
        print(f"    Max:    {max(times):.3f}")
        if len(times) > 1:
            print(f"    StdDev: {statistics.stdev(times):.3f}")
        print(f"  Peak memory (KB):")
        print(f"    Mean: {sum(memories) / len(memories):.1f}")
        print(f"  Communication(bytes):")
        print(f"    Mean: {sum(bandwidths) / len(bandwidths):.0f}")
        print(f"{'=' * 60}\n")
