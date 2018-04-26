import socket
import threading

from ts4mp.debug.log import ts4mp_log
from ts4mp.core.mp_essential import outgoing_lock, outgoing_commands
from ts4mp.core.networking import generic_send_loop, generic_listen_loop


class Server:
    def __init__(self):
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.host = ""
        self.port = 9999
        self.serversocket.bind((self.host, self.port))
        self.clientsocket = None

    def listen(self):
        threading.Thread(target=self.listen_loop, args=[]).start()

    def send(self):
        threading.Thread(target=self.send_loop, args=[]).start()

    def send_loop(self):
        while True:
            if self.clientsocket is not None:
                ts4mp_log("locks", "acquiring outgoing lock")

                with outgoing_lock:
                    for data in outgoing_commands:
                        generic_send_loop(data, self.clientsocket)
                        outgoing_commands.remove(data)

                ts4mp_log("locks", "releasing outgoing lock")

            # time.sleep(1)

    def listen_loop(self):
        global incoming_commands

        self.serversocket.listen(5)
        self.clientsocket, address = self.serversocket.accept()

        ts4mp_log("network", "Client Connect")

        clientsocket = self.clientsocket
        size = None
        data = b''

        while True:
            # output_irregardelessly("network", "Server Listen Update")
            # TODO: Is this supposed to override the global variable? It's really unclear
            incoming_commands, data, size = generic_listen_loop(clientsocket, incoming_commands, data, size)
            # time.sleep(1)