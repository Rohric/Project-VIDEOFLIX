from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings

from .models import User


@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    """Send activation email to new users. Triggered on User.save() with created=True."""
    if not created:
        return

    token = default_token_generator.make_token(instance)
    uidb64 = urlsafe_base64_encode(force_bytes(instance.pk))
    activation_link = f"{settings.FRONTEND_URL}/activate/{uidb64}/{token}/"

    subject = "Activate Your Account"
    message = f"""Hello {instance.email},

Welcome to our platform! Click the link below to activate your account:

{activation_link}

If you didn't sign up for this account, please ignore this email.

Best regards,
The Team"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [instance.email],
        fail_silently=True,
    )
