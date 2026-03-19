import threading
from dataclasses import replace
from framework.communication import ChannelPair
from framework.benchmark import BandwidthTracker

bw = BandwidthTracker()
pair = ChannelPair(bandwidth_tracker=bw)

# Run sender/receiver in separate threads (mimicking a real protocol)
results = {}

def sender_side():
    pair.sender.send({"message": "hello from sender"}, label="greeting")
    reply = pair.sender.receive(label="reply")
    results["sender_got"] = reply

def receiver_side():
    msg = pair.receiver.receive(label="greeting")
    results["receiver_got"] = msg
    pair.receiver.send("got it, thanks", label="greeting")

t1 = threading.Thread(target=sender_side)
t2 = threading.Thread(target=receiver_side)
t1.start()
t2.start()
t1.join()
t2.join()

print(f"Receiver got: {results['receiver_got']}")
print(f"Sender got: {results['sender_got']}")
print(f"Bytes exchanged: {bw.total_bytes}")
print(f"Messages: {bw.message_count}")

