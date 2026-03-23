# OT Benchmark - Post-Quantum Oblivious Transfer Comparison

Empirical benchmarking framework comparing two post-quantum OT paradigms for my BSc dissertation "A Systematic Evaluation of 
Information-Theoretic vs Lattice-Based Post-Quantum Oblivious Transfer
"

## Protocols

- **Lattice OT** (Dong et al.) - Mod-LWR based, computational security from lattice hardness
- **Supersonic OT** (Abadi & Desmedt) - Information-theoretic security via trusted dealer and XOR

## Project Structure
```
ot_benchmark/
├── protocols/           
│     ├── lattice_ot/          # Mod-LWR lattice-based OT    
│     └── supersonic_ot/       # Supersonic OT with trusted dealer
├── framework/
│     ├── benchmark.py         # Timing, memory, bandwidth instruments
│     ├── communication.py     # In-process + socket message passing
│     └── metrics.py           # Metric collection and CSV export
├── experiments/               # Experiment runners (TODO)
├── results/logs/              # Experiment output
``` 

## Setup
```
pip install numpy cryptodome psutil
```

## Running Tests
```
python test_lattice_ot.py
python test_supersonic_ot.py
```