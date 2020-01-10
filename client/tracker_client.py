import time
import json
from threading import Thread
from tcp_connection import TcpConnection

class TrackerClient(Thread):

    def __init__(self, my_id, info_hash, ip, port, tracker_ip, tracker_port, main_controller):
        super(TrackerClient, self).__init__()
        self.my_id = my_id
        self.info_hash = info_hash
        self.ip = ip
        self.port = port
        self.tracker_ip = tracker_ip
        self.tracker_port = tracker_port
        self.main_controller = main_controller
        
    def run(self):
        data = {}
        data['info_hash'] = self.info_hash
        data['peer_id'] = self.my_id
        data['ip'] = self.ip
        data['port'] = self.port
        data['event'] = 'start'
        
        
        tcp_connection = TcpConnection()
        try:
            tcp_connection.connect(self.tracker_ip, self.tracker_port)
            tcp_connection.send(json.dumps(data).encode('utf-8'))
            response_message = json.loads(tcp_connection.receive().decode('utf-8'))
            tcp_connection.close()
        except Exception as e:
            print(e)
            tcp_connection.close()
            self.main_controller.tell({
                'header' : 13,
                'body' : 'Connection error with tracker'
            })
            return
        
        if response_message['status_code'] == '0':
            self.main_controller.tell({
                'header' : 13,
                'body' : 'Received status code 0 from tracker'
            })
            return

        self.main_controller.tell({
            'header' : 9,
            'body' : response_message['peers']
        })
        
        interval = int(float(response_message['interval'])/1000) - 1
        data['event'] = 'update'

        while True:
            time.sleep(interval)
            try:
                tcp_connection = TcpConnection()
                tcp_connection.connect(self.tracker_ip, self.tracker_port)
                tcp_connection.send(json.dumps(data).encode('utf-8'))
                response_message = json.loads(tcp_connection.receive().decode('utf-8'))
                tcp_connection.close()
            except Exception as e:
                print(e)
                tcp_connection.close()
                self.main_controller.tell({
                    'header' : 13,
                    'body' : 'Connection error with tracker'
                })
                return

            if response_message['status_code'] == '0':
                self.main_controller.tell({
                    'header' : 13,
                    'body' : 'Received status code 0 from tracker'
                })
                return

            self.main_controller.tell({
                'header' : 9,
                'body' : response_message['peers']
            })

