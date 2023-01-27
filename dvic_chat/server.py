import argparse
import socket
from threading import Thread
from time import sleep
import traceback

from dvic_chat.protocol import DataStream, Packet1Auth, Packet2Message

class ChatClient():
    def __init__(self, sck: socket.socket, addr, srv: "DVICChatServer") -> None:
        self.socket = sck
        self.address = addr
        self.username = None
        self.server: "DVICChatServer" = srv
        self.data_stream = DataStream(self.socket)
        self.start_client_threads()

    def start_client_threads(self):
        Thread(target=self._client_receive_thread_target, daemon=True).start()

    def _client_receive_thread_target(self):
        while True:
            try:
                # read packet id
                pck_id = self.data_stream.receive_int()
                if pck_id == 1:
                    # packet 1 Auth
                    self._handle_packet1_auth(Packet1Auth().receive(self.data_stream))
                elif pck_id == 2:
                    # packet 2 Message
                    self._handle_packet2_message(Packet2Message().receive(self.data_stream))
                else:
                    print(f"Protocol error with client {self.address}")
                    self.socket.close()
            except:
                    print(f"Rcv thread error with client {self.address}")
                    traceback.print_exc()
                    try: 
                        self.socket.close()
                    except: pass # socket may be already closed but we make sure
                    self.server.client_disconnected(self)
                    return
            
    def send_message(self, raw_message: str):
        try:
            Packet2Message(raw_message).send(self.data_stream)
        except:
            traceback.print_exc()
            self.socket.close()

    @property
    def name(self) -> str:
        if self.username is None: return "[unknown]"
        return self.username

    def set_client_name(self, name: str):
        self.username = name

    def _handle_packet1_auth(self, pck):
        self.set_client_name(pck.name)
        self.srv.broadcast(f'{self.name} has entered the chat')

    def _handle_packet2_message(self, pck):
        if self.name == "unknown":
            print("!!! Client tried to send a message before authentication")
            self.socket.close()
            return
        self.server.broadcast(f'{self.name}: {pck.message}')

class DVICChatServer:
    def __init__(self, port: int = 5432) -> None:
        self.listen_addr = ("0.0.0.0", port)
        self.clients: list[ChatClient] = []

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(self.listen_addr)
        self.server_socket.listen(3)
        Thread(target=self._accept_connection_thread_target, daemon=True).start()
        self._handle_console_input()

    def setup_client_connection(self, sck, addr):
        client: ChatClient = ChatClient(sck, addr, self)
        self.clients.append(client)

    def client_disconnected(self, client: ChatClient):
        if client in self.clients:
            self.clients.remove(client)
            self.broadcast(f'{client.name} ({client.address} disconnected.')

    def broadcast(self, raw_message: str, loopback = True):
        for c in self.clients:
            c.send_message(raw_message)
        if loopback:
            print(raw_message)
        
    def disconnect(self, client: ChatClient):
        client.socket.close()

    def _handle_console_input(self):
        while True:
            try:
                inp = input()
                self.broadcast(f'[console] {inp}', loopback=False)
            except KeyboardInterrupt:
                self.broadcast(f'[console] Server closing')
                self.server_socket.close()
                # sleep(.5)
                exit(0)

    def _accept_connection_thread_target(self):
        print("Waiting for connections")
        while True:
            client_sck, client_addr = self.server_socket.accept()
            print(f"Connection from {client_addr}")
            self.setup_client_connection(client_sck, client_addr)



if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument('--port', '-p', type=int, required=True)
    args = args.parse_args()
    DVICChatServer(args.port).start_server()