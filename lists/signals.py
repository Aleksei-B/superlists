from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.contrib.auth import get_user_model
User = get_user_model()
from notifications.signals import notify
from lists.models import List


@receiver(m2m_changed, sender=List.shared_with.through)
def user_shares_list(instance, pk_set, action, **kwargs):
    if action == 'post_add':
        notify.send(
            sender=instance.owner, recipient=User.objects.get(email=pk_set.pop()),
            verb='shared a list', action_object=instance
        )
