"""
Communication layer for OT protocol message exchange

Provides two backends:
- InProcessChannel: direct message parsing (pure computation benchmarks)
- SocketChannel: TCP sockets (real network latency measurement)

Both share the same interface so protocol code works with either
"""

import pickle
import socket
import threading
from abc import ABC, abstractmethod
from typing import Any, Optional
from .benchmark import BandwidthTracker


# Abstract interface that both channel types implement
class Channel(ABC):

    @abstractmethod
    def send(self, data: Any, label: str = "") -> Any:
        pass

    @abstractmethod
    def receive(self, label: str = "") -> Any:
        pass


# In-process message passing using a shared buffer, they are serialized with pickle to measure realistic byte sizes.

class InProcessChannel(Channel):

    def __init__(self, bandwidth_tracker: Optional[BandwidthTracker] = None):
        self._buffer: list[bytes] = []
        self._lock = threading.Lock()
        self._event = threading.Event()
        self._bandwidth_tracker = bandwidth_tracker or BandwidthTracker()

    def send(self, data: Any, label: str = "") -> None:
        raw = pickle.dumps(data)
        self._bandwidth_tracker.record_sent(raw)
        with self._lock:
            self._buffer.append(raw)
            self._event.set()

    def receive(self, label: str = "") -> Any:
        while True:
            with self._lock:
                if self._buffer:
                    raw = self._buffer.pop(0)
                    if not self._buffer:
                        self._event.clear()
                    self._bandwidth_tracker.record_received(raw)
                    return pickle.loads(raw)
                self._event.wait(timeout=0.01)


# Creates a linked pair of channels for sender/receiver
class ChannelPair:

    def __init__(self, bandwidth_tracker: Optional[BandwidthTracker] = None):
        self.bandwidth_tracker = bandwidth_tracker or BandwidthTracker()
        self._ch_s2r = InProcessChannel(self.bandwidth_tracker)
        self._ch_r2s = InProcessChannel(self.bandwidth_tracker)

    @property
    def sender(self) -> Channel:
        return _PairedChannel(self._ch_s2r, self._ch_r2s)

    @property
    def receiver(self) -> Channel:
        return _PairedChannel(self._ch_r2s, self._ch_s2r)


# One side of a paired in-process channel
class _PairedChannel(Channel):

    def __init__(self, send_ch: InProcessChannel, recv_ch: InProcessChannel):
        self._send_ch = send_ch
        self._recv_ch = recv_ch

    def send(self, data: Any, label: str = "") -> None:
        self._send_ch.send(data, label)

    def receive(self, label: str = "") -> Any:
        return self._recv_ch.receive(label)


# TCP socket-based communication, to be implemented later on

class SocketChannel(Channel):

    def send(self, data: Any, label: str = "") -> None:
        raise NotImplementedError("Socket channel not implemented yet")

    def receive(self, label: str = "") -> Any:
        raise NotImplementedError("Socket channel not implemented yet")




