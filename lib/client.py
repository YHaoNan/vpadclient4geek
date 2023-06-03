import socket
from lib.constants import *

"""
Not Thread Safe
"""
class Client:
    def __init__(self, host):
        self.host = host
        self.is_used = False

    def connect(self, timeout=2):
        if self.is_used:
            raise "Cannot reuse client, please create another!"
        try:
            self.conn = socket.create_connection((self.host, SERVER_PORT), timeout=timeout)
            self.is_used = True
            return True
        except:
            return False
    
    def close(self):
        if self.conn:
            self.conn.close()
    
    def send(self, message):
        self.conn.send(bytes(message.bytes()))