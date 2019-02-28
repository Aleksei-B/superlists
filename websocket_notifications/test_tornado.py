import unittest
from unittest.mock import Mock, patch
from collections import defaultdict

from websockets_notifications.tornado import NotificationsHandler


@patch.dict(NotificationsHandler.clients)
class NotificationsHandlerTest(unittest.TestCase):

    def test_open_saves_current_list_id(self):
        client = Mock()  # NotificationsHandler instance
        current_list = 'list_id'
        
        NotificationsHandler.open(client, current_list)
        self.assertEqual(client.current_list, current_list)       

    def test_open_saves_clients_using_current_list_id_as_key(self):
        client = Mock()  # NotificationsHandler instance
        current_list = 'list_id'
        
        NotificationsHandler.open(client, current_list)
        self.assertEqual(
            NotificationsHandler.clients[current_list].pop(),
            client
        )
        
    def test_on_close_deletes_saved_client(self):
        other_client = Mock()      #
        client_to_delete = Mock()  # NotificationsHandler instances
        other_client.current_list = 'list_id'
        client_to_delete.current_list = 'list_id'
        NotificationsHandler.clients['list_id'].update(
            [other_client, client_to_delete]
        )
        
        NotificationsHandler.on_close(client_to_delete)
        self.assertEqual(
            len(NotificationsHandler.clients['list_id']),
            1
        )
        self.assertEqual(
            NotificationsHandler.clients['list_id'].pop(),
            other_client
        )
        
    def test_broadcast_sends_update_message_to_current_list_users(self):
        user, user2 = Mock(), Mock()
        user3, user4 = Mock(), Mock()
        NotificationsHandler.clients['first_list'].update([user, user2])
        NotificationsHandler.clients['second_list'].update([user3, user4])
        message = 'update'
        current_list_key = 'second_list'
        
        NotificationsHandler.broadcast(message, current_list_key)
        user3.write_message.assert_called_once_with(message)
        user4.write_message.assert_called_once_with(message)
        user.write_message.assert_not_called
        user2.write_message.assert_not_called
