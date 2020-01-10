import threading

class PiecesMap():

    def __init__(self, piece_length):
        self.pieces_dict = {}
        self.piece_length = piece_length
        self.lock = threading.Lock()
    
    def add_piece(self, index, length, hash, state):
        with self.lock:
            self.pieces_dict[index] = {'length' : length, 'hash' : hash, 'state' : state}
    
    def contains_piece(self, index):
        with self.lock:
            return index in self.pieces_dict
    
    def get_size(self):
        with self.lock:
            return len(self.pieces_dict)
    
    def get_piece(self, index):
        with self.lock:
            if index not in self.pieces_dict:
                raise Exception('piece not present')
            return self.pieces_dict[index]

    def get_downloaded_pieces(self):
        with self.lock:
            return [key for key, value in self.pieces_dict.items() if value['state'] == 'downloaded']
    
    def set_piece_requested(self, index):
        with self.lock:
            if index not in self.pieces_dict:
                raise Exception('piece not present')
            if self.pieces_dict[index]['state'] == 'requested':
                raise IsRequestedStateException()
            elif self.pieces_dict[index]['state'] == 'downloaded':
                raise IsDownloadedStateException()
            self.pieces_dict[index]['state'] = 'requested'
    
    def set_piece_downloaded(self, index):
        with self.lock:
            if index not in self.pieces_dict:
                raise Exception('piece not present')
            if self.pieces_dict[index]['state'] == 'missing':
                raise IsMissingStateException()
            elif self.pieces_dict[index]['state'] == 'downloaded':
                raise IsDownloadedStateException()
            self.pieces_dict[index]['state'] = 'downloaded'

    def set_piece_missing(self, index):
        with self.lock:
            if index not in self.pieces_dict:
                raise Exception('piece not present')
            if self.pieces_dict[index]['state'] == 'missing':
                raise IsMissingStateException()
            elif self.pieces_dict[index]['state'] == 'downloaded':
                raise IsDownloadedStateException()
            self.pieces_dict[index]['state'] = 'missing'
    
    def is_piece_downloaded(self, index):
        with self.lock:
            return self.pieces_dict[index]['state'] == 'downloaded'


class IsMissingStateException(Exception):
    pass

class IsRequestedStateException(Exception):
    pass

class IsDownloadedStateException(Exception):
    pass