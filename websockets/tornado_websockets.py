from collections import defaultdict

import tornado.ioloop
from tornado.web import RequestHandler, Application
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

            
class NotifyApi(RequestHandler):

    def post(self):
        message = self.get_body_argument('message')
        list_id = self.get_body_argument('list_id')
        NotifyHandler.broadcast(message, list_id)
        
        
def make_app():
    app =  Application([(r'/ws', NotifyHandler)])
    app.add_handlers(
        r'(localhost|127\.0\.0\.1)', [('/wsapi', NotifyApi)]
     )
    return app
    

if __name__ == '__main__':
    application = make_app()
    loop = tornado.ioloop.IOLoop.current()
    try:
        print("Starting server")
        application.listen(8000)
        loop.start()
    except KeyboardInterrupt:
        loop.stop()       # might be redundant, the loop has already stopped
        loop.close(True)  # needed to close all open sockets
        print("Server shut down, exiting...")
