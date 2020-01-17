
import pykka
import hashlib
import random
import sys
from config import CODE_SIZE, TIMER_INTERVAL, UNCHOCKED_PEERS
from peer import Peer
from tcp_connection import TcpConnection
from file_object import FileObject
from pieces_map import PiecesMap
from timer import Timer

import logging
logging.basicConfig(level=logging.DEBUG)

class MainController(pykka.ThreadingActor):

    def __init__(self, my_id, info_hash, torrent_file_data, seeder):
        super().__init__()
        self.my_id = my_id
        self.info_hash = info_hash
        self.peers = {}
        self.pieces_map = PiecesMap(torrent_file_data['info']['piece_length'])

        hashes = torrent_file_data['info']['pieces']
        tokens = [(hashes[i:i+40]) for i in range(0, len(hashes), 40)]
        
        if seeder is True:
            self.file_object = FileObject(open(torrent_file_data['info']['name'],'rb'))
            self.build_pieces_dict(self.pieces_map, torrent_file_data['info']['length'], torrent_file_data['info']['piece_length'], tokens, 'downloaded')
        else:
            self.file_object = FileObject(open(torrent_file_data['info']['name'],'w+b',0))
            self.file_object.write(torrent_file_data['info']['length']-1, b'\x00')
            self.build_pieces_dict(self.pieces_map, torrent_file_data['info']['length'], torrent_file_data['info']['piece_length'], tokens, 'missing')
            
    def build_pieces_dict(self, pieces_map, file_length, piece_length, tokens, pieces_state):
        for index in range(0, int(file_length/piece_length)):
            pieces_map.add_piece(index, piece_length, tokens[index],pieces_state)
        
        if file_length % piece_length != 0:
            pieces_map.add_piece(int(file_length/piece_length), file_length % piece_length, tokens[-1], pieces_state)
        
    def piece(self, message_body):
        index = message_body['index']
        peer_id = message_body['peer_id']
        self.peers[peer_id]['downloaded_bytes'] += self.pieces_map.get_piece(index)['length']
        for peer in self.peers.values():
            peer['actor_ref'].tell({
                'header' : 10,
                'body' : index
            })
        if len(self.pieces_map.get_downloaded_pieces()) == self.pieces_map.get_size():
            print('Downloaded all pieces')
                    
    def add_peer(self, message_body):
        peer_id = message_body[0]
        tcp_connection = message_body[1]
        
        if peer_id != self.my_id and peer_id not in self.peers:
            peer = Peer.start(peer_id, tcp_connection, self.actor_ref, self.file_object, self.pieces_map)
            self.peers[peer_id] = {'actor_ref' : peer, 'downloaded_bytes' : 0, 'state' : 'not_interested'}
            print(f'added new peer with id: {peer_id}')
            if len(self.peers) == 1:
                self.timer = Timer(TIMER_INTERVAL, self.actor_ref)
                self.timer.daemon = True
                self.timer.start()
            
    
    def add_peers(self, message_body):
        for peer_data in message_body.values():
            try:
                if peer_data['id'] != self.my_id and peer_data['id'] not in self.peers:
                    tcp_connection = TcpConnection()
                    tcp_connection.connect(peer_data['ip'], peer_data['port'])
                    tcp_connection.send((19).to_bytes(CODE_SIZE, byteorder='big')+(self.info_hash+self.my_id).encode('utf-8'))

                    if int.from_bytes(tcp_connection.receive(), byteorder='big') == 11:
                        peer = Peer.start(peer_data['id'], tcp_connection, self.actor_ref, self.file_object, self.pieces_map)
                        self.peers[peer_data['id']] = {'actor_ref' : peer, 'downloaded_bytes' : 0, 'state' : 'not_interested'}
                        print(f"added new peer with id: {peer_data['id']}")
                        if len(self.peers) == 1:
                            self.timer = Timer(TIMER_INTERVAL, self.actor_ref)
                            self.timer.daemon = True
                            self.timer.start()
            except:
                pass

    def chocking_algorithm(self, message_body):
        def downloaded_bytes(peer):
            return peer['downloaded_bytes']
        
        peers_list = [peer for peer in self.peers.values() if peer['state'] == 'interested']
        ordered_peers_list = sorted([peer for peer in peers_list if peer['downloaded_bytes'] > 0], key=downloaded_bytes, reverse = True)

        for peer in ordered_peers_list[0:min(len(ordered_peers_list), UNCHOCKED_PEERS)]:
            #Peer unchocked
            peer['actor_ref'].tell({
                'header' : 9,
                'body' : None
            })
            peers_list.remove(peer)

        if len(peers_list) > 0:
            #Optimistic unchoked peer
            peer = random.choice(peers_list)
            peer['actor_ref'].tell({
                'header' : 9,
                'body' : None
            })
            peers_list.remove(peer)
        
        for key, peer in self.peers.items():
            #Peer chocked
            if peer in peers_list:
                peer['actor_ref'].tell({
                    'header' : 8,
                    'body' : None
                })
            self.peers[key]['downloaded_bytes'] = 0
    
    def interested(self, message_body):
        self.peers[message_body]['state'] = 'interested'
    
    def not_interested(self, message_body):
        self.peers[message_body]['state'] = 'not_interested'

    def peer_failure(self, message_body):
        print(f'Stopping {message_body}')
        self.peers[message_body]['actor_ref'].stop()
        del self.peers[message_body]
        print(f'Removed {message_body}')
        if len(self.peers) == 0:
            self.timer.stop()
            
    def stop(self, message_body):
        for peer in self.peers:
            peer['actor_ref'].stop()
        self.file_object.close()
        sys.exit(message_body)

    def handle_message(self, message_header, message_body):
        switcher = {
            2 : self.interested,
            3 : self.not_interested, 
            7 : self.piece,
            8 : self.add_peer,
            9 : self.add_peers,
            10 : self.chocking_algorithm,
            12 : self.peer_failure,
            13 : self.stop
        }
        
        function=switcher.get(message_header,lambda :'Invalid message header')
        function(message_body)

    def on_receive(self, message):
        self.handle_message(message['header'], message['body'])
    
