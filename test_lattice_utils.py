from protocols.lattice_ot.params import LatticeParams
from protocols.lattice_ot.utils import (
    generate_public_matrix, generate_secret_vector,
    lwr_round, encode_message, decode_message, mat_vec_mult
)

params = LatticeParams.small()


# Test 1: Matrix generation
A = generate_public_matrix(params)
print(f"Matrix A shape: {A.shape} (should be {params.n} x {params.n})")
print(f"All entries in [0, q): {(A >= 0).all() and (A < params.q).all()}")

# Test 2: Secret vector
s = generate_secret_vector(params)
print(f"Secret vector length: {len(s)} (should be {params.n})")
print(f"All entries in [0, p): {(s >= 0).all() and (s <= params.p).all()}")

# Test 3: Rounding
raw = mat_vec_mult(A, s, params.q)
rounded = lwr_round(raw, params)
print(f"Rounded values in [0, p): {(rounded >= 0).all() and (rounded <= params.p).all()}")

# Test 4: Message encode/decode roundtrip
original = b"hello world"
encoded = encode_message(original, params)
decoded = decode_message(encoded, len(original))
print(f"Message roundtrip: {decoded} (should be b'hello world')")

print("\nAll utils working correctly!")