"""
Sender side of Supersonic OT

Uses dealer provided pads to encrypt both messages.
Only XOR operations, no public key maths required.
"""

from .params import SupersonicParams

class SupersonicOTSender:

    def __init__(self, params: SupersonicParams):
        self.params = params

    # Encrypt both messages with dealer shares and receiver masked bit
    def encrypt(self, sender_shares: dict, e: int, m0: bytes,
                m1: bytes) -> dict:
        assert e in (0, 1), "e must be 0 or 1"

        k_e = sender_shares[f"k{e}"]
        k_not_e = sender_shares[f"k{1 - e}"]

        c0 = bytes(a ^ b for a, b in zip(m0, k_e))
        c1 = bytes(a ^ b for a, b in zip(m1, k_not_e))

        return {"c0": c0, "c1": c1}