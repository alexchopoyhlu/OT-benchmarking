"""
Receiver side of Supersonic OT.

Uses dealer provided shares to mask the choice bit
and decrypt the chosen message.
"""

from .params import SupersonicParams

class SupersonicOTReceiver:

    def __init__(self, params: SupersonicParams):
        self.params = params

    # Mask the choice bit with the dealer's random bit
    def mask_choice(self, choice_bit: int, receiver_shares: dict) -> int:
        assert choice_bit in (0, 1), "Chouce bit must be 0 or 1"
        self.choice_bit = choice_bit
        self.receiver_shares = receiver_shares

        e = choice_bit ^ receiver_shares["d"]
        return e

    # Decrypt chosen message
    def decrypt(self, ciphertext: dict) -> bytes:
        d = self.receiver_shares["d"]
        k_d = self.receiver_shares["k_d"]
        b = self.choice_bit

        e = b ^ d
        if d == e:
            cb = ciphertext["c0"]
        else:
            cb = ciphertext["c1"]

        recovered = bytes(a ^ b for a, b in zip(cb, k_d))
        return recovered