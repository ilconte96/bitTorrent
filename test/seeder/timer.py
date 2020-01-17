import socket
import time
from threading import Thread

class Timer(Thread):
    def __init__(self, interval, main_controller):
        super(Timer, self).__init__()
        self.interval = interval
        self.main_controller = main_controller
        self.clear = True
        
    def run(self):
        self.clear = False
        while True:
            time.sleep(self.interval)
            if self.clear is True:
                break
            self.main_controller.tell({
                'header' : 10,
                'body' : None,
            })
    
    def stop(self):
        self.clear = True