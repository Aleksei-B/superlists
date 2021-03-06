import unittest
from unittest.mock import Mock, patch
import urllib.parse

from tornado.testing import AsyncHTTPTestCase
from websockets.tornado_websockets import NotifyHandler, make_app


@patch.dict(NotifyHandler.clients)
class NotifyHandlerTest(unittest.TestCase):

    def test_open_saves_current_list_id(self):
        client = Mock()  # NotifyHandler instance
        current_list = 'list_id'
        
        NotifyHandler.open(client, current_list)
        self.assertEqual(client.current_list, current_list)       

    def test_open_saves_clients_using_current_list_id_as_key(self):
        client = Mock()  # NotifyHandler instance
        current_list = 'list_id'
        
        NotifyHandler.open(client, current_list)
        self.assertEqual(
            NotifyHandler.clients[current_list].pop(),
            client
        )
        
    def test_on_close_deletes_saved_client(self):
        other_client = Mock()      #
        client_to_delete = Mock()  # NotifyHandler instances
        other_client.current_list = 'list_id'
        client_to_delete.current_list = 'list_id'
        NotifyHandler.clients['list_id'].update(
            [other_client, client_to_delete]
        )
        
        NotifyHandler.on_close(client_to_delete)
        self.assertEqual(
            len(NotifyHandler.clients['list_id']),
            1
        )
        self.assertEqual(
            NotifyHandler.clients['list_id'].pop(),
            other_client
        )
        
    def test_broadcast_sends_update_message_to_current_list_users(self):
        user, user2 = Mock(), Mock()
        user3, user4 = Mock(), Mock()
        NotifyHandler.clients['first_list'].update([user, user2])
        NotifyHandler.clients['second_list'].update([user3, user4])
        message = 'update'
        current_list_key = 'second_list'
        
        NotifyHandler.broadcast(message, current_list_key)
        user3.write_message.assert_called_once_with(message)
        user4.write_message.assert_called_once_with(message)
        user.write_message.assert_not_called
        user2.write_message.assert_not_called
        
        
class NotifyApiTest(AsyncHTTPTestCase):

    def get_app(self):
        return make_app()
        
    @patch('websockets.tornado_websockets.NotifyHandler.broadcast')
    def test_post_should_call_broadcast_with_correct_args(
        self, mock_broadcast
    ):
        post_data = {'message': 'update', 'list_id': '1234'}
        body = urllib.parse.urlencode(post_data)
        self.fetch('/wsapi', method='POST', body=body)
        mock_broadcast.assert_called_once_with('update', '1234')
