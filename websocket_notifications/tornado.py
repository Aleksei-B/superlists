from collections import defaultdict

from tornado.websocket import WebSocketHandler


class NotifyHandler(WebSocketHandler):

    clients = defaultdict(set)
    
    def __init__(self):
        super().__init__()
        self.current_list = None

    def open(self, current_list):
        self.current_list = current_list
        NotifyHandler.clients[current_list].add(self)
        
    def on_close(self):
        NotifyHandler.clients[self.current_list].discard(self)
        
    @classmethod
    def broadcast(cls, message, list_key):
        for client in cls.clients[list_key]:
            client.write_message(message)
