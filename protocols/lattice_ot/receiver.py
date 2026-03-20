"""
Receiver side of the Mod-LWR Lattice OT protocol

The receiver has a choice bit b and constructs a public
key that lets them decrypt only message m_b. The sender
cannot determine which message was chosen.
"""

import numpy
import numpy as np

from .params import LatticeParams
from .utils import (
    generate_secret_vector, generate_public_matrix, lwr_round, decode_message, mat_vec_mult
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

        pk_real = np.zeros((n, n), dtype=np.int64)
        for i in range(n):
            pk_real[i] = mat_vec_mult(
                public_matrix,
                (self.secret * (i + 1)) % q,
                q
            )

        pk_fake = np.random.randint(0, q, size=(n, n), dtype=np.int64)

        pk = np.zeros((2, n, n), dtype=np.int64)
        pk[choice_bit] = pk_real
        pk[1 - choice_bit] = pk_fake

        self._pk_real = pk_real

        return pk


    # Decrypt the chosen message from the sender's ciphertexts
    def decrypt(self, ciphertext: dict, num_bytes: int) -> numpy.ndarray:
        p = self.params.p
        q = self.params.q
        b = self.choice_bit

        u = ciphertext["u"]
        cb = ciphertext[f"c{b}"]

        mask = np.zeros(self.params.n, dtype=np.int64)
        for i in range(self.params.n):
            scaled_secret = (self.secret * (i + 1)) % q
            dot = np.sum(scaled_secret.astype(object) * u.astype(object)) % p
            mask[i] = dot % p

        recovered = (cb - mask) % p
        return decode_message(recovered, num_bytes)
