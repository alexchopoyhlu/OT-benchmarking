"""
Supersonic OT Parameters

Simpler than lattice OT, no modular arithmetic needed.
The main parameter is just the message size, since the
protocol operates on raw bytes with XOR.
"""

from dataclasses import dataclass

@dataclass
class SupersonicParams:
    message_bytes: int = 16

    def __post_init__(self):
        assert self.message_bytes > 0, "message_bytes must positive"

    @classmethod
    def small(cls):
        return cls(message_bytes=4)

    @classmethod
    def medium(cls):
        return cls(message_bytes=16)

    @classmethod
    def large(cls):
        return cls(message_bytes=256)