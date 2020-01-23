from config import CODE_SIZE
from threading import Thread
from pykka import ActorDeadError

class PeerConnectionReader(Thread):

    def __init__(self, tcp_connection, peer):
        super(PeerConnectionReader, self).__init__()
        self.tcp_connection = tcp_connection
        self.peer = peer
        
    def stop(self):
        self.clear = True
    
    def run(self):
        self.clear = False
        while self.clear is False:
            try:
                self.tcp_connection.wait_readable_data()
                message = self.tcp_connection.receive()
                self.peer.tell({
                    'header' : int.from_bytes(message[0:CODE_SIZE], byteorder='big'),
                    'body' : message[CODE_SIZE:]
                })
            except Exception as e:
                try:
                    self.peer.tell({
                        'header' : 12,
                        'body' : None
                    })
                except ActorDeadError as e:
                    print(e)
                break
