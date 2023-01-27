import struct
import socket

class DataStream:
    def __init__(self, socket: socket.socket) -> None:
        self.sck = socket

    def send_int(self, i: int):
        self.sck.send(bytes(i))
    
    def receive_int(self) -> int:
        return int(self.sck.recv(struct.calcsize('i')))

    def send_str(self, s: str):
        bs = s.encode('utf-8')
        self.send_int(len(bs))
        self.sck.send(bs)
    
    def receive_str(self) -> int:
        l = self.receive_int()
        return self.sck.recv(l).decode('utf-8')


class Packet:
    def __init__(self, packet_id: int) -> None:
        self.packet_id: int = packet_id

    def send(self, data_stream: DataStream):
        data_stream.send_int(self.packet_id)
    
    def receive(self, data_stream: DataStream):
        raise NotImplementedError()
    
class Packet1Auth(Packet):

    def __init__(self, name: str = None) -> None:
        super().__init__(1)
        self.name = name

    def send(self, data_stream: DataStream):
        super().send(data_stream)
        data_stream.send_str(self.name)
    
    def receive(self, data_stream: DataStream):
        self.name = data_stream.receive_str()
        return self

class Packet2Message(Packet):
    def __init__(self, msg: str = None) -> None:
        super().__init__(2)
        self.message = msg

    def send(self, data_stream: DataStream):
        super().send(data_stream)
        data_stream.send_str(self.message)
    
    def receive(self, data_stream: DataStream):
        self.message = data_stream.receive_str()
        return self