from protocols.lattice_ot import LatticeOTSender, LatticeOTSender, LatticeOTSender, LatticeParams, LatticeOTReceiver

params = LatticeParams.small()

# Messages the sender holds
m0 = b"secrete message zero"
m1 = b"secrete message one"

# Test with choice bit = 0
print("=== Test: choice_bit = 0 ===")
receiver = LatticeOTReceiver(params)
sender = LatticeOTSender(params)

public_matrix = receiver.setup()
receiver_pk = receiver.generate_keys(choice_bit=0, public_matrix=public_matrix)
ciphertext = sender.encrypt(public_matrix, receiver_pk, m0, m1)
result = receiver.decrypt(ciphertext, len(m0))
print(f"Receiver wanted m0: {m0}")
print(f"Receiver got:       {result}")
print(f"Correct: {result == m0}")

# Test with choice bit = 1
print("\n=== Test: choice_bit = 1 ===")
receiver2 = LatticeOTReceiver(params)
sender2 = LatticeOTSender(params)

public_matrix2 = receiver2.setup()
receiver_pk2 = receiver2.generate_keys(choice_bit=1, public_matrix=public_matrix2)
ciphertext2 = sender2.encrypt(public_matrix2, receiver_pk2, m0, m1)
result2 = receiver2.decrypt(ciphertext2, len(m1))
print(f"Sender wanted m1: {m1}")
print(f"Sender got:       {result2}")
print(f"Correct: {result2 == m1}")