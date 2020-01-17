import threading
import os

class FileObject():

    def __init__(self, file_object):
        self.file_object = file_object
        self.lock = threading.Lock()
    
    def read(self, position, bytes_number):
        with self.lock:
            if self.file_object is None:
                return
            self.file_object.seek(position)
            return self.file_object.read(bytes_number)
        
    def write(self, position, bytes_stream):
        with self.lock:
            if self.file_object is None:
                return
            self.file_object.seek(position)
            self.file_object.write(bytes_stream)
    
    def close(self):
        with self.lock:
            if self.file_object is None:
                return
            self.file_object.close()
            self.file_object = None