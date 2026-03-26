if __name__ == "__main__":
    from framework.communication import create_socket_pair
    from framework.communication import BandwidthTracker

    bw = BandwidthTracker()
    sender_ch, receiver_ch = create_socket_pair(bandwidth_tracker=bw)

    # Sender sends a message
    sender_ch.send({"msg": "hello over TCP"}, label="test")

    # Receiver reads it
    result = receiver_ch.receive(label="test")
    print(f"Received: {result}")

    # Receiver replies
    receiver_ch.send({"reply from receiver"}, label="reply")
    reply = sender_ch.receive(label="reply")
    print(f"Reply: {reply}")

    print(f"Bytes exchanged: {bw.total_bytes}")
    print(f"Messages: {bw.message_count}")

    sender_ch.close()
    receiver_ch.close()

    print("Socket communication working!")