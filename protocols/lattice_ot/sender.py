"""
Sender side of the Mod-LWR Lattice OT protocol.

The sender holds two messages (m0, m1) and encrypts both
using the receiver's public key. Only the message corresponding
to the receiver's secret choice bit can be decrypted.
"""

import numpy as np
from .params import LatticeParams
from .utils import generate_secret_vector, lwr_round, encode_message, mat_vec_mult


class LatticeOTSender:

    def __init__(self, params: LatticeParams):
        self.params = params

    # Encrypt both messages under the receiver's public key
    def encrypt(self, public_matrix: np.ndarray, receiver_pk: np.ndarray,
                m0: bytes, m1: bytes) -> dict:
        p = self.params.p
        q = self.params.q
        n = self.params.n

        r = generate_secret_vector(self.params)

        a_transpose_r = mat_vec_mult(public_matrix.T, r, q)
        u = lwr_round(a_transpose_r, self.params)

        m0_encoded = encode_message(m0, self.params)
        m1_encoded = encode_message(m1, self.params)

        pk0 = receiver_pk[0]
        pk1 = receiver_pk[1]

        pk0_r = mat_vec_mult(pk0, r, q)
        pk1_r = mat_vec_mult(pk1, r, q)

        c0 = (lwr_round(pk0_r, self.params) + m0_encoded) % p
        c1 = (lwr_round(pk1_r, self.params) + m1_encoded) % p

        return {"u": u, "c0": c0, "c1": c1}