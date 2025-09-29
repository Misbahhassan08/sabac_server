from django.db.models.signals import post_save
from django.dispatch import receiver

from .firebase_utils import send_fcm_notification
from .models import Notification, User


@receiver(post_save, sender=User)
def send_notification_to_admins(sender, instance, created, **kwargs):
    """Send notification to all admins when a new user registers"""
    if created:
        # get all admin device tokens
        admins = Notification.objects.filter(role="admin")

        for admin in admins:
            send_fcm_notification(
                admin.device_token,
                role="admin",
                title="New User Registered",
                body=f"{instance.name} has just registered!",
            )
        dealers = Notification.objects.filter(role="dealer")

        for dealer in dealers:
            send_fcm_notification(
                dealer.device_token,
                role="dealer",
                title="hello dealer",
                body=f"{instance.name} has just registered!",
            )
        inspectors = Notification.objects.filter(role="inspector")

        for inspector in inspectors:
            send_fcm_notification(
                inspector.device_token,
                role="inspector",
                title="hello inspector",
                body=f"{instance.name} has just registered!",
            )
