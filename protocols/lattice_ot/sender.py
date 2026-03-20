"""
Sender side of the Mod-LWR Lattice OT protocol.

The sender holds two messages (m0, m1) and encrypts both
using the receiver's public key. Only the message corresponding
to the receiver's secret choice bit can be decrypted.
"""

import hashlib
import numpy as np
from .params import LatticeParams
from .utils import generate_secret_vector, mat_vec_mult


class LatticeOTSender:

    def __init__(self, params: LatticeParams):
        self.params = params

    # Encrypt both messages under the receiver's public key
    def encrypt(self, public_matrix: np.ndarray, receiver_pk: dict,
                m0: bytes, m1: bytes) -> dict:

        q = self.params.q

        r = generate_secret_vector(self.params)

        u = mat_vec_mult(public_matrix.T, r, q)

        pk0 = receiver_pk[0]
        pk1 = receiver_pk[1]

        shared0 = int(np.sum(pk0.astype(object) * r.astype(object)) % q)
        shared1 = int(np.sum(pk1.astype(object) * r.astype(object)) % q)

        pad0 = self._hash_to_pad(shared0, len(m0))
        pad1 = self._hash_to_pad(shared1, len(m1))

        c0 = bytes(a ^ b for a, b in zip(m0, pad0))
        c1 = bytes(a ^ b for a, b in zip(m1, pad1))

        return {"u": u, "c0": c0, "c1": c1}

    def _hash_to_pad(self, shared_value: int, length: int) -> bytes:
        h = hashlib.shake_256(str(shared_value).encode())
        return h.digest(length)