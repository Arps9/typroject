"""Notification services - thin facade over the model."""
from __future__ import annotations

from django.core.mail import send_mail
from django.conf import settings

from apps.core.enums import NotificationChannel

from .models import Notification


def notify(user, title: str, body: str = "", *, link: str = "",
           channel: str = NotificationChannel.IN_APP) -> Notification:
    notif = Notification.objects.create(
        user=user, title=title, body=body, link=link, channel=channel,
    )
    if channel in {NotificationChannel.EMAIL, NotificationChannel.BOTH} and user.email:
        try:
            send_mail(
                subject=title,
                message=body or title,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:  # pragma: no cover
            pass
    return notif
