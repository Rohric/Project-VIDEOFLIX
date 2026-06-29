import logging
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
import uuid

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_save, sender=User)
def send_verification_email(sender, instance, created, **kwargs):
    """Send verification email when new user registers."""
    if created and not instance.is_active:
        # Generate verification token
        token = str(uuid.uuid4())
        instance.verification_token = token
        instance.save(update_fields=["verification_token"])

        # Build verification link
        verify_link = f"http://localhost:5500/verify-email/?token={token}&user_id={instance.pk}"

        try:
            send_mail(
                subject="Verify your email address",
                message=f"Click here to verify: {verify_link}",
                from_email="noreply@videoflix.com",
                recipient_list=[instance.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Failed to send verification email to {instance.email}: {str(e)}")
