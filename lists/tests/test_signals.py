from unittest.mock import patch, Mock
from django.test import TestCase
from django.contrib.auth import get_user_model
User = get_user_model()
from lists.models import List
from lists.signals import invalidate_list_cache


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
