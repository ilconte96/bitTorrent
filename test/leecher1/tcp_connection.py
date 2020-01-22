import socket
import select
from config import BUFFER_SIZE,HEADER_SIZE,SOCKET_READ_TIMEOUT,SOCKET_WAIT_TIMEOUT

class TcpConnection():

    def __init__(self, client_socket = None):
        if client_socket is None:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.client_socket = client_socket
        self.client_socket.settimeout(SOCKET_READ_TIMEOUT)
    
    def connect(self, ip, port):
        self.client_socket.connect((ip, port))

    def send(self, byte_stream):
        byte_stream_length = len(byte_stream)
        self.client_socket.send(byte_stream_length.to_bytes(HEADER_SIZE, byteorder='big'))

        for i in range(0, int(byte_stream_length/BUFFER_SIZE)):
            self.client_socket.send(byte_stream[(i*BUFFER_SIZE):(i*BUFFER_SIZE)+BUFFER_SIZE])
        
        if byte_stream_length % BUFFER_SIZE !=0:
            self.client_socket.send(byte_stream[byte_stream_length-byte_stream_length % BUFFER_SIZE:byte_stream_length])
    
    def receive(self):
        byte_stream_length = int.from_bytes(self.client_socket.recv(HEADER_SIZE), byteorder='big')
        byte_stream = bytes()
        
        if byte_stream_length == 0:
            raise Exception('Error in read from socket')
        else:
            for _ in range(0, int(byte_stream_length/BUFFER_SIZE)):
                byte_stream += self.client_socket.recv(BUFFER_SIZE)

            if byte_stream_length % BUFFER_SIZE !=0:
                byte_stream += self.client_socket.recv(byte_stream_length % BUFFER_SIZE)

            return byte_stream
    
    def wait_readable_data(self):
        readable_sockets, _, exception_sockets = select.select([self.client_socket], [], [self.client_socket], SOCKET_WAIT_TIMEOUT)
        if len(exception_sockets) > 0:
            raise Exception('Connection error')
        if len(readable_sockets) == 0:
            raise Exception('Connection wait timeout')

    def close(self):
        self.client_socket.close()