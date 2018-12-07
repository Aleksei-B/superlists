from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.contrib.auth import get_user_model
User = get_user_model()
from notifications.signals import notify
from lists.models import List, Item


@receiver(m2m_changed, sender=List.shared_with.through)
def user_shares_list(instance, pk_set, action, **kwargs):
    if action == 'post_add':
        notify.send(
            sender=instance.owner, recipient=User.objects.get(email=pk_set.pop()),
            verb='shared a list', action_object=instance
        )


@receiver(post_save, sender=Item)
def invalidate_list_cache(instance, **kwargs):
    key = make_template_fragment_key('item_list', [instance.list.pk])
    cache.delete(key)
