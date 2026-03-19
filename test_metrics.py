from framework.metrics import MetricsCollector, TrialResult

collector = MetricsCollector("test_experiment")

# Simulate 5 trials with fake data
for i in range(5):
    result = TrialResult(
        protocol_name="test_protocol",
        trial_number=i,
        message_bits=128,
        execution_time_ms=10.5 + i * 0.3,
        sender_time_ms=256.0 + i * 10,
        bytes_sent=1024 + i * 50,
        bytes_received=512 + i * 25,
        message_count=3,
        correct=True,
    )
    collector.add_result(result)

# Test summary output
collector.print_summary()

# Test CSV export
collector.export_csv("results/logs/test_results.csv")

# Check CSV was created
with open("results/logs/test_results.csv") as f:
    print(f"\nCSV contents:\n{f.read()}")