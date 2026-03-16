"""
Benchmarking instrumentation for OT protocol evaluation.

Provides three measurement tools that wrap around protocol execution:
- BenchmarkTimer: exectuion timing (high resolution)
- MemoryTracker: peak memory usage tracking (tracemalloc)
- BandwidthTracker: communication overhead tracking (bytes sent/received)
"""

import time
import tracemalloc
from dataclasses import dataclass

# Measures execution time using the highest resolution monotonic clock
@dataclass
class BenchmarkTimer:
    _start_ns: int = 0
    _end_ns: int = 0

    @property
    def elapsed_ns(self):
        return self._end_ns - self._start_ns

    @property
    def elapsed_ms(self):
        return self.elapsed_ns / 1_000_000

    @property
    def elapsed_s(self):
        return self.elapsed_ms / 1_000_000_000

    def __enter__(self):
        self._start_ns = time.perf_counter_ns()
        return self

    def __exit__(self, *args):
        self._end_ns = time.perf_counter_ns()


# Tracks peak memory allocation during protocol execution
@dataclass
class MemoryTracker:
    peak_bytes: int = 0
    current_bytes: int = 0

    @property
    def peak_kb(self):
        return self.peak_bytes / 1024

    @property
    def peak_mb(self):
        return self.peak_bytes / (1024 * 1024)

    def __enter__(self):
        if tracemalloc.is_tracing():
            tracemalloc.stop()
        tracemalloc.start()
        return self

    def __exit__(self, *args):
        self.current_bytes, self.peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()



# Counts bytes exchanged between the sender and receiver
@dataclass
class BandwidthTracker:
    bytes_sent: int = 0
    bytes_received: int = 0
    message_count: int = 0

    def record_sent(self, data: bytes):
        self.bytes_sent += len(data)
        self.message_count += 1

    def record_received(self, data: bytes):
        self.bytes_received += len(data)

    @property
    def total_bytes(self):
        return self.bytes_sent + self.bytes_received

    @property
    def total_sent_kb(self):
        return self.bytes_sent / 1024

    @property
    def total_received_kb(self):
        return self.bytes_received / 1024

    def reset(self):
        self.bytes_sent = 0
        self.bytes_received = 0
        self.message_count = 0