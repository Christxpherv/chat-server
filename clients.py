import socket
import sys
import threading
import configparser
import uuid
import os
import time
import ssl

from typing import Tuple

from Thread.threading import ChatThread
from Interface.GUI import GUI


class ChatClient:
    def __init__(self):
        # Create variables to be used later
        self.identifier = str(uuid.uuid4())
        self.sock = socket.socket()
        self.username = self.identifier
        self.encoding = 'utf-8'
        self.disconnect_event = threading.Event()
        self.connected = False

        # Fetch the host and port from the get_config function
        self.host, self.port, self.debug = self.get_config()
        
        # Create SSL context
        context = ssl.create_default_context(cafile='./SSL/server.crt')
        self.secureSock = context.wrap_socket(self.sock, server_hostname=self.host)

        # Set the username
        self.username = self.identifier

        # Create a thread for processing messages
        self.chat_thread = ChatThread(func=self.receive_messages)

        global current_client
        current_client = self

        # start the GUI
        self.gui = GUI(self, self.debug)
        self.gui.start_chatting()

    def receive_messages(self):
        try:
            last_data = current_client.secureSock.recv(1024)

            if last_data:
                last_message = last_data.decode(self.encoding)
                if last_message == '%IDENTIFY':
                    current_client.secureSock.send(current_client.username.encode(self.encoding))
                else:
                    current_client.gui.message_received(last_message)
            else:
                os.close(current_client.secureSock.fileno())

        except Exception as err:
            print(err)
            current_client.gui.quit()

    def send_message(self, next_message):
        while True:
            if next_message == '.quit' or next_message == '.exit':
                self.secureSock.send("has disconnected".encode(self.encoding))
                self.gui.quit()
            else:
                encoded_message = next_message.encode(self.encoding)

                self.secureSock.send(encoded_message)
                self.debug_print("Sending message: %s" % encoded_message)
            break

    @staticmethod
    def get_config() -> Tuple[str, int, bool]:
        config = configparser.ConfigParser()
        config.read('config.ini')

        true_values = ['yes', 'true']

        if 'client' in config:
            host = "localhost"
            port = 1222
            debug = False

            return host, port, debug
        else:
            exit(2)

    def start_chatting(self, username):
        try:
            self.username = username
            self.secureSock.connect((self.host, self.port))

            self.debug_print("Starting chatting with username: %s" % username)

            self.chat_thread.start()
            self.connected = True

        except Exception as e:
            print(e)
            self.gui.show_error(e, "Could not connect to server")
            self.gui.request_username()

    def quit(self):
        self.disconnect_event.set()
        self.secureSock.close()
        self.debug_print("Quitting...")
        time.sleep(1)

        self.disconnect_event.set()

        if self.connected is True:
            self.chat_thread.stop()

        self.connected = False
        sys.exit()

    def debug_print(self, debug_msg):
        if self.debug:
            print("DBG: %s" % debug_msg)


current_client: ChatClient

if __name__ == '__main__':
    chat_client = None

    try:
        chat_client = ChatClient()
    except KeyboardInterrupt:
        pass
    finally:
        if chat_client is not None:
            chat_client.quit()
            sys.exit()