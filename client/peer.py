import pykka
import hashlib
import random
import logging
from config import CODE_SIZE, INDEX_SIZE
from termcolor import colored
from pieces_map import IsDownloadedStateException, IsRequestedStateException
from peer_connection_reader import PeerConnectionReader

class Peer(pykka.ThreadingActor):

    def __init__(self, id, tcp_connection, main_controller, file_object, pieces_map):
        super().__init__()
        self.id = id
        self.tcp_connection = tcp_connection
        self.main_controller = main_controller
        self.file_object = file_object
        self.pieces_map = pieces_map
        self.pieces_number = self.pieces_map.get_size()
        self.piece_length = self.pieces_map.piece_length
        self.pieces_indexes_queue = []
        self.am_unchoked = False
        self.is_unchoked = False
        self.requested_piece = None
        self.peer_connection_reader = PeerConnectionReader(self.tcp_connection, self.actor_ref)
        self.peer_connection_reader.start()
        self.send_bitfield()
    
    def choke(self, message_body):
        print(colored(f'Received chocke message from {self.id}','red'))
        self.am_unchoked = False

    def unchoke(self, message_body):
        print(colored(f'Received unchoke message from {self.id}','green'))
        self.am_unchoked = True
        
    def send_choke(self, message_body):
        self.is_unchoked = False
        try:
            self.tcp_connection.send((0).to_bytes(CODE_SIZE, byteorder='big'))
        except Exception as e:
            print(e)
            print(colored(f'Error in sending choke to {self.id}','red'))
            pass
        
    def send_unchoke(self, message_body):
        self.is_unchoked = True
        try:
            self.tcp_connection.send((1).to_bytes(CODE_SIZE, byteorder='big'))
        except Exception as e:
            print(e)
            print(colored(f'Error in sending unchoke to {self.id}','red'))
            pass
    
    def interested(self, message_body):
        self.main_controller.tell({
            'header' : 2,
            'body' : self.id
        })
    
    def not_interested(self, message_body):
        self.send_choke(None)
        self.main_controller.tell({
            'header' : 3,
            'body' : self.id
        })
    
    def send_interested(self):
        try:
            print(colored(f'Sending interested message to {self.id}','cyan'))
            self.tcp_connection.send((2).to_bytes(CODE_SIZE, byteorder='big'))
        except Exception as e:
            print(e)
            print(colored(f'Error in sending interested message to {self.id}','red'))
            pass
    
    def send_not_interested(self):
        try:
            print(colored(f'Sending not interested message to {self.id}','cyan'))
            self.tcp_connection.send((3).to_bytes(CODE_SIZE, byteorder='big'))
        except Exception as e:
            print(e)
            print(colored(f'Error in sending not interested message to {self.id}','red'))
            pass
    
    def have(self, message_body):
        index = int.from_bytes(message_body[0:INDEX_SIZE], byteorder='big')
        print(colored(f'Received have for index {index} from {self.id}','cyan'))
        if self.pieces_map.contains_piece(index) and not index in self.pieces_indexes_queue and not self.pieces_map.is_piece_downloaded(index):
            self.pieces_indexes_queue.append(index)
            if len(self.pieces_indexes_queue) == 1:
                self.send_interested()
            print(colored(f'Added in queue piece {index} received from {self.id}','cyan'))
        
    def send_have(self, index):
        print(colored(f'Sending have to {self.id}','cyan'))
        try:
            if index in self.pieces_indexes_queue:
                self.pieces_indexes_queue.remove(index)
                if len(self.pieces_indexes_queue) == 0:
                    self.send_not_interested()
            self.tcp_connection.send((4).to_bytes(CODE_SIZE, byteorder='big') + (index).to_bytes(INDEX_SIZE, byteorder='big'))
        except Exception as e:
            print(colored(f'Error in sending have to {self.id}','red'))
            print(e)
            pass
        
    def bitfield(self, message_body):
        bitfield = message_body
        for index in range(0,len(bitfield)):
            if bitfield[index] == 1:
                if self.pieces_map.contains_piece(index) and not index in self.pieces_indexes_queue and not self.pieces_map.is_piece_downloaded(index):
                    self.pieces_indexes_queue.append(index)
        random.shuffle(self.pieces_indexes_queue)
        if len(self.pieces_indexes_queue) > 0:
            self.send_interested()
        
    def send_bitfield(self):
        bitfield = bytes()
        for index in range(0, self.pieces_number):
            if index in self.pieces_map.get_downloaded_pieces():
                bitfield += (1).to_bytes(1, byteorder='big')
            else:
                bitfield += (0).to_bytes(1, byteorder='big')
        print(colored(f'Sending bitfield to {self.id}','cyan'))
        try:
            self.tcp_connection.send((5).to_bytes(CODE_SIZE, byteorder='big') + bitfield)
        except Exception as e:
            print(colored(f'Error in send bitfield to {self.id}','red'))
            print(e)
            pass
    
    def send_request(self, index):
        try:
            self.tcp_connection.send((6).to_bytes(CODE_SIZE, byteorder='big') + (index).to_bytes(INDEX_SIZE, byteorder='big'))
        except Exception as e:
            print(colored(f'Error in sending request of index {index} to {self.id}','red'))
            print(e)
            pass
        self.requested_piece = index
        print(colored(f'Requested piece with index {index} to {self.id}','cyan'))
    
    def request(self, message_body):
        try:
            if self.is_unchoked is False:
                print(colored(f'Cannot serve request from {self.id} because this peer is chocked','red'))
                self.tcp_connection.send((11).to_bytes(CODE_SIZE, byteorder='big'))
            else:
                index = int.from_bytes(message_body, byteorder='big')
                if index not in self.pieces_map.get_downloaded_pieces():
                    self.tcp_connection.send((11).to_bytes(CODE_SIZE, byteorder='big'))
                else:
                    print(colored(f'Received request for piece with index {index}','cyan'))
                    self.tcp_connection.send((7).to_bytes(CODE_SIZE, byteorder='big') + (index).to_bytes(INDEX_SIZE, byteorder='big') + self.file_object.read(index * self.piece_length, self.pieces_map.get_piece(index)['length']))
        except Exception as e:
            print(e)
            pass

    def request_error(self, message_body):
        print(colored(f'Received request error message from {self.id}','red'))
        if self.requested_piece is not None:
            self.pieces_indexes_queue.append(self.requested_piece)
            self.pieces_map.set_piece_missing(self.requested_piece)
            self.requested_piece = None
        
    def connection_error(self, message_body):
        print(colored(f'Connection error with peer {self.id}','red'))
        self.main_controller.tell({
            'header' : 12,
            'body' : self.id
        })
    
    def piece(self, message_body):
        index = int.from_bytes(message_body[0:INDEX_SIZE], byteorder='big')
        if index == self.requested_piece:
            piece = self.pieces_map.get_piece(index)
            
            if piece['hash'] != hashlib.sha1(message_body[INDEX_SIZE:]).hexdigest():
                print(colored(f'Received invalid piece of index {index} from {self.id}','red'))
                self.main_controller.tell({
                    'header' : 12,
                    'body' : self.id
                })
            else:
                print(colored(f'Received valid piece of index {index}','green'))
                self.file_object.write(index*self.piece_length, message_body[INDEX_SIZE:])
                self.pieces_map.set_piece_downloaded(index)
                self.main_controller.tell({
                    'header' : 7,
                    'body' : {'index' : index, 'peer_id' : self.id}
                })
                
                self.requested_piece = None
                if len(self.pieces_indexes_queue) == 0:
                    self.send_not_interested()
    
    def process_pieces_queue(self):
        if self.requested_piece is None:
            if len(self.pieces_indexes_queue) > 0:
                index = self.pieces_indexes_queue.pop(0)
                try:
                    self.pieces_map.set_piece_requested(index)
                    self.send_request(index)
                except IsRequestedStateException:
                    self.pieces_indexes_queue.append(index)
                    print(colored(f'Piece with index {index} just requested','red'))
                except IsDownloadedStateException:
                    if len(self.pieces_indexes_queue) == 0:
                        self.send_not_interested()
                    print(colored(f'Piece with index {index} just downloaded','red'))
                except Exception as e:
                    print(e)
    
    def handle_message(self, message_header, message_body):
        switcher = { 
            0 : self.choke,
            1 : self.unchoke,
            2 : self.interested,
            3 : self.not_interested,
            4 : self.have,
            5 : self.bitfield,
            6 : self.request,
            7 : self.piece,
            8 : self.send_choke,
            9 : self.send_unchoke,
            10 : self.send_have,
            11 : self.request_error,
            12: self.connection_error
        }

        function=switcher.get(message_header,lambda :'Invalid message header')
        function(message_body)
    
    def on_stop(self):
        if self.requested_piece is not None:
            self.pieces_map.set_piece_missing(self.requested_piece)
            self.requested_piece = None
        self.peer_connection_reader.stop()
        self.tcp_connection.close()
        self.peer_connection_reader.join()
        print(colored(f'Connection closed','red'))

    def on_receive(self, message):
        message_header = message['header']
        message_body = message['body']

        self.handle_message(message_header, message_body)

        if self.am_unchoked is True and message_header != 12:
            self.process_pieces_queue()