import argparse
import socket
from threading import Thread
from dvic_chat.protocol import DataStream, Packet1Auth, Packet2Message

class DVICChatClient():
    def __init__(self, address: str, port: int, username: str) -> None:
        self.username: str = username
        self.data_stream: DataStream = None
        self.socket: socket.socket = None
        self.address: str = address
        self.port: int = port

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.address, self.port))
        self.data_stream = DataStream(self.socket)
        self.authenticate()
        Thread(target = self._receive_packets_target, daemon=True).start()
        return True

    def authenticate(self):
        Packet1Auth(self.username).send(self.data_stream)

    def _receive_packets_target(self):
        while True:
            try:

                #receive packet id
                pck_id = self.data_stream.receive_int()
                if pck_id == 2:
                    p = Packet2Message().receive(self.data_stream)
                    print(p.message) # handle here
                else:
                    print("Protocol error")
                    raise RuntimeError("Protocol Error")
            except:
                try:
                    self.socket.close()
                except: pass
                print("Disconnected from server")
                exit(1)
                


    def send_message(self, message: str):
        Packet2Message(message).send(self.data_stream)

    def handle_console_input(self):
        while True:
            inp = input()
            print(f'\r{" "*len(inp)}')
            Packet2Message(inp).send(self.data_stream)

if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("--username", "-u", required=True, type=str)
    args.add_argument("--host", "-a", required=True, type=str)
    args.add_argument("--port", "-p", required=True, type=int)
    args = args.parse_args()

    c = DVICChatClient(args.host, args.port, args.username)
    if c.connect():
        c.handle_console_input()

