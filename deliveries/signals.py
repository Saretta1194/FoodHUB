from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Delivery


@receiver(pre_save, sender=Delivery)
def _store_old_delivery_status(sender, instance: Delivery, **kwargs):
    if instance.pk:
        try:
            old = Delivery.objects.get(pk=instance.pk)
            instance._old_status = old.status
        except Delivery.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Delivery)
def _notify_delivery_status_change(sender, instance: Delivery, created, **kwargs):
    if created:
        return
    old = getattr(instance, "_old_status", None)
    if not old or old == instance.status:
        return

    order = instance.order
    recipient_list = (
        [order.user.email] if order and order.user and order.user.email else []
    )
    if not recipient_list:
        return

    status_lower = instance.status.replace("_", " ").lower()
    subject = f"Your order #{order.id} has been {status_lower}"
    message = f"Order #{order.id} status changed to {instance.status}."
    try:
        send_mail(
            subject,
            message,
            getattr(settings, "DEFAULT_FROM_EMAIL", None),
            recipient_list,
            fail_silently=True,
        )
    except Exception:
        pass
