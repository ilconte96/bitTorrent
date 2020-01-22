import os
import argparse
import json
import hashlib
import random
import string
import sys
from config import AUTHENTICATION_TOKEN_SIZE
from tcp_connection import TcpConnection

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file_path', type = str, required = True)
    parser.add_argument('--torrent_file_name', type = str, required = True)
    parser.add_argument('--tracker_ip', type = str, required = True)
    parser.add_argument('--tracker_port', type = int, required = True)
    parser.add_argument('--piece_length', type = int, default = 256)
    args = parser.parse_args()

    data = {}
    data['tracker_ip'] = args.tracker_ip
    data['tracker_port'] = args.tracker_port

    if not os.path.exists(args.input_file_path):
        sys.exit('File not exists')

    input_file_size = os.stat(args.input_file_path).st_size

    data['info'] = {}
    data['info']['length'] = input_file_size
    data['info']['name'] = os.path.basename(args.input_file_path)

    with open(args.input_file_path, 'rb') as input_file:
        hashes = str()
        for _ in range(0, int(input_file_size/args.piece_length)):
            hashes += hashlib.sha1(input_file.read(args.piece_length)).hexdigest()
        if input_file_size % args.piece_length != 0:
            hashes += hashlib.sha1(input_file.read(input_file_size % args.piece_length)).hexdigest()
        
    data['info']['piece_length'] = min(input_file_size, args.piece_length)
    data['info']['pieces'] = hashes
    data['info']['length'] = input_file_size

    with open(args.torrent_file_name, 'w') as torrent_file:
        torrent_file.write(json.dumps(data))

    json_data = {}
    json_data['info_hash'] = hashlib.sha1(json.dumps(data['info']).encode('utf-8')).hexdigest()
    json_data['authentication_token'] = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(AUTHENTICATION_TOKEN_SIZE))
    json_data['event'] = 'add'

    request_message = json.dumps(json_data)
    try:
        send_message_to_tracker(request_message, args.tracker_ip, args.tracker_port)
    except:
        print('Error in sending data to tracker')


def send_message_to_tracker(request_message,tracker_ip,tracker_port):
    tcp_connection = TcpConnection()
    tcp_connection.connect(tracker_ip, tracker_port)
    tcp_connection.send(request_message.encode('utf-8'))
    response_message = tcp_connection.receive().decode('utf-8')
    print(response_message)

if __name__ == '__main__':
    main()
