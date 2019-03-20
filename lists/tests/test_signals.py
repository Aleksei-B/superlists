from unittest.mock import patch, Mock
from urllib.parse import urlencode

from django.test import TestCase
from django.contrib.auth import get_user_model
User = get_user_model()

from lists.models import List, Item
from lists.signals import invalidate_list_cache


TORNADO_API_URL = 'http://127.0.0.1/wsapi'


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


@patch('lists.signals.cache')
@patch('lists.signals.make_template_fragment_key')
class InvalidateListCacheTest(TestCase):

    def test_should_call_make_template_fragment_key_with_right_arguments(
        self, mock_make_template_fragment_key, mock_cache
    ):
        instance = Mock()
        invalidate_list_cache(instance=instance)
        mock_make_template_fragment_key.assert_called_once_with(
            'item_list', [instance.list.pk]
        )

    def test_should_call_cache_delete_with_correct_key(
        self, mock_make_template_fragment_key, mock_cache
    ):
        instance = Mock()
        mock_make_template_fragment_key.return_value = 'abcde'
        invalidate_list_cache(instance)
        mock_cache.delete.assert_called_once_with('abcde')


@patch('lists.signals.urlopen')
class WebsocketBroadcastTest(TestCase):

    def test_should_POST_to_correct_url(self, mock_urlopen):
        owner = User.objects.create(email='owner@example.com')
        list_ = List.objects.create(owner=owner)
        item = Item.objects.create(list=list_)

        correct_url = TORNADO_API_URL
        (request, ), _ = mock_urlopen.call_args
        self.assertEqual(request.full_url, correct_url)
        self.assertEqual(request.get_method(), 'POST')

    def test_should_send_correct_data(self, mock_urlopen):
        owner = User.objects.create(email='owner@example.com')
        list_ = List.objects.create(owner=owner)
        item = Item.objects.create(list=list_)
        
        correct_data = urlencode(
            {'message': 'update', 'list_id': list_.id}
        )
        (request, ), _ = mock_urlopen.call_args
        self.assertEqual(request.data, correct_data)
        
    def test_should_POST_only_if_list_have_an_owner(self, mock_urlopen):
        list_ = List.objects.create(owner=None)
        item = Item.objects.create(list=list_)
        
        mock_urlopen.assert_not_called()
