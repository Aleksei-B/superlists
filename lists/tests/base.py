from django.test import TestCase
from django.db.models import signals

from lists.signals import websocket_broadcast
from lists.models import Item


class IntegrationTest(TestCase):

    @classmethod
    def setUpClass(cls):
        signals.post_save.disconnect(
            receiver=websocket_broadcast,
            sender=Item
        )
        
    @classmethod
    def tearDownClass(cls):
        signals.post_save.connect(
            receiver=websocket_broadcast,
            sender=Item
        )
