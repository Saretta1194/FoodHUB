from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Order

@receiver(pre_save, sender=Order)
def _store_old_status(sender, instance: Order, **kwargs):
    if instance.pk:
        try:
            old = Order.objects.get(pk=instance.pk)
            instance._old_status = old.status
        except Order.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None

@receiver(post_save, sender=Order)
def _notify_order_status_change(sender, instance: Order, created, **kwargs):
    if created:
        return
    old = getattr(instance, "_old_status", None)
    if not old or old == instance.status:
        return

    subj = f"Your order #{instance.id} status changed: {instance.status}"
    msg = f"Order #{instance.id} is now {instance.status}."
    to = [instance.user.email] if instance.user and instance.user.email else []
    if to:
        try:
            send_mail(subj, msg, getattr(settings, "DEFAULT_FROM_EMAIL", None), to, fail_silently=True)
        except Exception:
            pass
