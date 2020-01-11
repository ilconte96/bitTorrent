import json
import argparse
import hashlib
import random
import string
import socket
from config import PEER_ID_SIZE
from tracker_client import TrackerClient
from tcp_server import TcpServer
from main_controller import MainController

def parse_torrent_file(torrent_file_path):
    with open(torrent_file_path, 'r') as torrent_file:
        return json.loads(torrent_file.read())

parser = argparse.ArgumentParser()
parser.add_argument('--torrent_file_path', type = str, required = True)
parser.add_argument('--seeder', action='store_true')
args = parser.parse_args()
torrent_file_data = parse_torrent_file(args.torrent_file_path)

info_hash = hashlib.sha1(json.dumps(torrent_file_data['info']).encode('utf-8')).hexdigest()
my_id = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(PEER_ID_SIZE))

main_controller = MainController.start(my_id, info_hash, torrent_file_data, args.seeder)
        
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((socket.gethostname(),0))
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.listen(5)

tracker_client = TrackerClient(my_id, info_hash, server_socket.getsockname()[0], server_socket.getsockname()[1], torrent_file_data['tracker_ip'], torrent_file_data['tracker_port'], main_controller)
tracker_client.daemon = True
tracker_client.start()

tcp_server = TcpServer(info_hash, server_socket, main_controller)
tcp_server.daemon = True
tcp_server.start()

    


