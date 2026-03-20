"""
Mod-LWR Lattice OT Parameters

Defines key parameters for the Dong et al. protocol,
controlling security, efficiency, and correctness.

Key parameters:
- n: lattice dimension (security parameter)
- q: main modulus (computations in Z_q)
- p: smaller modulus for rounding (p < q)
- message_bits: size of OT messages
"""

from dataclasses import dataclass

@dataclass
class LatticeParams:
    n: int = 256
    q: int = 7681
    p: int = 256
    message_bits: int = 128

    def __post_init__(self):
        assert self.q > self.p, "q must be larger than p"
        assert self.p > 1, "p must be at least 2"
        assert self.message_bits > 0, "message_bits must be positive"
        assert self.n > 0, "dimension n must be positive"


    # Small parameters for quick testing
    @classmethod
    def small(cls):
        return cls(n=64, q=7681, p=256, message_bits=32)

    # Medium parameters for benchmarking
    @classmethod
    def medium(cls):
        return cls(n=256, q=7681, p=256, message_bits=128)

    # Large parameters for scalability testing
    @classmethod
    def large(cls):
        return cls(n=512, q=7681, p=256, message_bits=256)