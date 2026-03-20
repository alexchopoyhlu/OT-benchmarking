"""
Receiver side of the Mod-LWR Lattice OT protocol

The receiver has a choice bit b and constructs a public
key that lets them decrypt only message m_b. The sender
cannot determine which message was chosen.
"""

import hashlib
import numpy as np
from .params import LatticeParams
from .utils import (
    generate_secret_vector, generate_public_matrix, mat_vec_mult
)

class LatticeOTReceiver:

    def __init__(self, params: LatticeParams):
        self.params = params

    # Generate the shared public matrix A
    def setup(self) -> np.ndarray:
        self.public_matrix = generate_public_matrix(self.params)
        return self.public_matrix

    # Generate the receiver's public key pair based on choice bit
    def generate_keys(self, choice_bit: int, public_matrix: np.ndarray) -> dict:
        assert choice_bit in (0, 1), "Choice bit must be 0 or 1"

        n = self.params.n
        q = self.params.q

        self.choice_bit = choice_bit
        self.secret = generate_secret_vector(self.params)

        pk_real = mat_vec_mult(public_matrix, self.secret, q)

        pk_fake = np.random.randint(0, q, size=n, dtype=np.int64)

        pk = {
            choice_bit: pk_real,
            1 - choice_bit: pk_fake
        }

        return pk


    # Decrypt the chosen message from the sender's ciphertexts
    def decrypt(self, ciphertext: dict, message_length: int) -> bytes:
        q = self.params.q
        b = self.choice_bit

        u = ciphertext["u"]
        cb = ciphertext[f"c{b}"]

        shared = int(np.sum(self.secret.astype(object) * u.astype(object)) % q)

        pad = self._hash_to_pad(shared, message_length)

        recovered = bytes(a ^ b for a, b in zip(cb, pad))

        return recovered

    def _hash_to_pad(self, shared_value: int, length: int) -> bytes:
        h = hashlib.shake_256(str(shared_value).encode())
        return h.digest(length)
