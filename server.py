import socket
import threading
import signal
import sys
import ssl
from datetime import datetime
from typing import Tuple


class ChatServer:
    def __init__(self):
        self.connections = []
        self.users = {}
        self.active = True

        self.stop_sock = threading.Event()
        self.host, self.port = self.get_config()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.context.load_cert_chain(certfile='./SSL/server.crt', keyfile='./SSL/server.key')
        self.secureSock = self.context.wrap_socket(self.sock, server_side=True)

    def start(self):
        try:
            self.secureSock.bind((self.host, self.port))
            self.secureSock.listen(4)

            ChatServer.print_log_line("Server ready to connect at %s:%d" % (self.host, self.port))

            while True:
                connection, address = self.secureSock.accept()
                connection.send("%IDENTIFY".encode('utf-8'))
                username = connection.recv(1024).decode('utf-8')

                self.users[self.address_key(address)] = username
                self.connections.append((connection, address))
                self.broadcast_message("New user connected: %s" % username)

                ChatServer.print_log_line("New user connected: %s" % username)

                threading.Thread(target=self.handler, args=[connection, address, self.stop_sock]).start()

        except Exception as e:
            print(e)
        finally:
            for connection, address in self.connections:
                self.terminate_connection(connection, address)

            self.secureSock.close()

    @staticmethod
    def get_config() -> Tuple[str, int]:
        port = 1222

        server = ''
        return server, port

    def send_to_peers(self, message: str, address: any, connection: socket.socket):
        for conn, _ in self.connections:
            if conn != connection:
                formatted_message = ("%s> %s" % (self.get_username(address), message))

                try:
                    conn.send(formatted_message.encode('utf-8'))

                except Exception as e:
                    ChatServer.print_log_line(e)
                    self.terminate_connection(conn, address)

    def handler(self, connection, address, stop_sock_event):
        while not stop_sock_event.is_set():
            try:
                data = connection.recv(1024)

                if data:
                    user_message = data.decode('utf-8')
                    self.send_to_peers(user_message, address, connection)
                else:
                    username = self.users[self.address_key(address)]
                    self.broadcast_message("%s has disconnected" % username)
                    ChatServer.print_log_line("%s has disconnected" % username)

                    self.terminate_connection(connection, address)
                    break

            except Exception as e:
                ChatServer.print_log_line(e)
                self.terminate_connection(connection, None)
                break

    def terminate_connection(self, connection: socket.socket, address: any):
        if (connection, address) in self.connections:
            connection.close()

            self.connections.remove((connection, address))

            if address:
                del self.users[self.address_key(address)]

    def broadcast_message(self, message: str):
        for conn, _ in self.connections:
            conn.send(message.encode('utf-8'))

    def stop_server(self, signum, frame):
        for connection, _ in self.connections:
            connection.close()

        self.users.clear()
        self.active = False
        self.secureSock.close()
        self.sock.close()
        self.stop_sock.set()
        ChatServer.print_log_line("Bye!!")
        sys.exit(0)

    @staticmethod
    def address_key(address):
        return str(address[0]) + '-' + str(address[1])

    def get_username(self, address):
        return self.users[self.address_key(address)]

    @staticmethod
    def print_log_line(message):
        dt_string = datetime.now().strftime("%d/%m/%Y %I:%M:%S %p")
        print(dt_string, "> ", message)


if __name__ == "__main__":
    server = ChatServer()

    signal.signal(signal.SIGINT, server.stop_server)
    server.start()
    signal.pause()
