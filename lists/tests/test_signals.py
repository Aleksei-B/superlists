from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
User = get_user_model()
from lists.models import List


class NotificationsTest(TestCase):

    @patch('notifications.notify.send')
    def test_user_shares_list_send_notify_signal(self, mock_notify_send):
        owner = User.objects.create(email='owner@example.com')
        sharee = User.objects.create(email='sharee@example.com')
        list_ = List.objects.create(owner=owner)
        list_.shared_with.add(sharee)

        mock_notify_send.assert_called_once()
        args, kwargs = mock_notify_send.call_args
        self.assertEqual(kwargs['sender'], owner)
        self.assertEqual(kwargs['recipient'], sharee)
        self.assertEqual(kwargs['action_object'], list_)
