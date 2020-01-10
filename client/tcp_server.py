import socket
import time
import json
from config import CODE_SIZE
from threading import Thread
from tcp_connection import TcpConnection

class TcpServer(Thread):
    def __init__(self, info_hash, server_socket, main_controller):
        super(TcpServer, self).__init__()
        self.info_hash = info_hash
        self.server_socket = server_socket
        self.main_controller = main_controller
    
    def handle_request(self, tcp_connection):
        
        message = tcp_connection.receive()
        handshake_code = int.from_bytes(message[0:CODE_SIZE],byteorder='big')
        
        if handshake_code != 19:
            return (False, None)

        info_hash = message[CODE_SIZE:CODE_SIZE+40].decode('utf-8')
        
        if info_hash != self.info_hash:
            return (False, None)

        return (True, message[CODE_SIZE+40:CODE_SIZE+60].decode('utf-8'))

    def run(self):
        while True:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"Connection from {address} has been established!")
                tcp_connection = TcpConnection(client_socket)
                status, peer_id = self.handle_request(tcp_connection)

                if status is True:
                    tcp_connection.send((11).to_bytes(CODE_SIZE, byteorder='big'))
                    self.main_controller.tell({
                        'header' : 8,
                        'body' : (peer_id, tcp_connection)
                    })
                else:
                    tcp_connection.send((12).to_bytes(CODE_SIZE, byteorder='big'))
                    tcp_connection.close()
            except Exception as e:
                print(e)
                tcp_connection.close()
