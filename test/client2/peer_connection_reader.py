from config import CODE_SIZE
from threading import Thread

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
                if len(message)<CODE_SIZE:
                    raise Exception('Unexpected message')
                self.peer.tell({
                    'header' : int.from_bytes(message[0:CODE_SIZE], byteorder='big'),
                    'body' : message[CODE_SIZE:]
                })
            except Exception as e:
                print(e)
                try:
                    self.peer.tell({
                        'header' : 12,
                        'body' : None
                    })
                except Exception as e:
                    print(e)
                break