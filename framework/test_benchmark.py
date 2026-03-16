from framework.benchmark import BenchmarkTimer, MemoryTracker, BandwidthTracker
import time

# Test 1: Timer
with BenchmarkTimer() as t:
    time.sleep(0.1)
print(f"Timer: {t.elapsed_ms:.1f} ms (should be ~100)")

# Test 2: Memory
with MemoryTracker() as m:
    big_list = [i for i in range(100000)]
print(f"Memory: {m.peak_kb:.1f} KB (should be > 0)")

# Test 3: Bandwidth
bw = BandwidthTracker()
bw.record_sent(b"hello")
bw.record_sent(b"world")
bw.record_received(b"response")

print(f"Sent: {bw.bytes_sent} bytes (should be 10)")
print(f"Messages: {bw.message_count} (should be 2)")
print(f"Total: {bw.total_bytes} bytes (should be 18)")

