"""
Lattice arithmetic utilities for Mod-LWR OT.

Provides the core mathematical operations:
- Random matrix/vector generation in Z_q
- Mod-LWR rounding function
- Message encoding/decoding to lattice elements
"""

import numpy as np
from .params import LatticeParams


# Generate a random n x n matrix with entries in Z_q
def generate_public_matrix(params: LatticeParams) -> np.ndarray:
    return np.random.randint(0, params.q, size=(params.n, params.n), dtype=np.int64)


# Generate a random secret vector with small entries
def generate_secret_vector(params: LatticeParams) -> np.ndarray:
    return np.random.randint(0, params.p, size=params.n, dtype=np.int64)


# Round from Z_q to Z_p (creating noise that hides the secret)
def lwr_round(value: np.ndarray, params: LatticeParams) -> np.ndarray:
    return ((params.p * value) // params.q) % params.p


# Convert a byte string message into a vector in Z_p
def encode_message(message: bytes, params: LatticeParams) -> np.ndarray:
    msg_array = np.frombuffer(message, dtype=np.uint8).astype(np.int64)
    result = np.zeros(params.n, dtype=np.int64)
    length = min(len(msg_array), params.n)
    result[:length] = msg_array[:length] % params.p
    return result


# Convert a vector in Z_p back to a byte string
def decode_message(vector: np.ndarray, num_bytes: int) -> bytes:
    clipped = np.clip(vector[:num_bytes], 0, 255).astype(np.uint8)
    return bytes(clipped)


# Compute a matrix at vector mod q
def mat_vec_mult(matrix: np.ndarray, vector: np.ndarray, q: int) -> np.ndarray:
    result = matrix.astype(object) @ vector.astype(object)
    return (np.array(result, dtype=object) % q).astype(np.int64)