from protocols.supersonic_ot import (
    SupersonicOTReceiver, SupersonicOTSender, Dealer, SupersonicOTSender, SupersonicParams
)

if __name__ == "__main__":

    params = SupersonicParams()

    m0 = b"\xaa\xbb\xcc\xdd"
    m1 = b"\x11\x22\x33\x44"

    # Run 10 times to test with different random dealer values
    all_correct = True
    for i in range(10):
        for choice in [0, 1]:
            dealer = Dealer(params)
            sender_shares, receiver_shares = dealer.generate_shares()

            receiver = SupersonicOTReceiver(params)
            sender = SupersonicOTSender(params)

            e = receiver.mask_choice(choice, receiver_shares)
            ciphertext = sender.encrypt(sender_shares, e, m0, m1)
            result = receiver.decrypt(ciphertext)

            expected = m0 if choice == 0 else m1
            if result != expected:
                print(f"FAIL: trial {i}, choice={choice}, got {result}, expected {expected.hex()}")
                all_correct = False

    if all_correct:
        print("All 20 tests passed (10 trials x 2 choice bits)")

    # Show one detailed run
    print("\n=== Detailed run: choice bit = 1 ===")
    dealer = Dealer(params)
    sender_shares, receiver_shares = dealer.generate_shares()
    print(f"Dealer d = {receiver_shares['d']}")
    print(f"Sender k0 = {sender_shares['k0'].hex()}")
    print(f"Sender k1 = {sender_shares['k1'].hex()}")
    print(f"Recevier k_d = {receiver_shares['k_d'].hex()}")

    receiver = SupersonicOTReceiver(params)
    sender = SupersonicOTSender(params)

    e = receiver.mask_choice(1, receiver_shares)
    print(f"Masked choice e = {e}")

    ciphertext = sender.encrypt(sender_shares, e, m0, m1)
    print(f"Decrypted: {result.hex()} (should be {m1.hex()})")
    print(f"Correct: {result == m1}")