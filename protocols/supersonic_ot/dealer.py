"""
Trusted dealer for Supersonic OT

Generates correlated random shares and distributes them
to sender and receiver before the transfer phase. The
dealer is only needed once, at the beginning.
"""

import os
from .params import SupersonicParams


class Dealer:
    def __init__(self, params: SupersonicParams):
        self.params = params

    # Generate correlated shares for sender and receiver
    def generate_shares(self) -> tuple[dict, dict]:

        # Random but
        d = int.from_bytes(os.urandom(1), 'big') % 2

        # 2 random pads
        k0 = os.urandom(self.params.message_bytes)
        k1 = os.urandom(self.params.message_bytes)

        sender_shares = {
            "k0": k0,
            "k1": k1,
        }

        receiver_shares = {
            "d": d,
            "k_d": k0 if d == 0 else k1,
        }

        return sender_shares, receiver_shares

