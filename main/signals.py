from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from .models import Reservation, OrderItem
from django.conf import settings


#======================================= Update total_amount ===============================================

@receiver(post_save, sender=OrderItem)
def update_order_totals(sender, instance, **kwargs):
    order = instance.order
    order.calculate_order_items()
    order.save()

#======================================= Update order_status ================================================

def mail_sender(subject, message, html_content, to):
    try:
        sending_from = settings.EMAIL_HOST_USER
        email = EmailMultiAlternatives(subject, message, sending_from, to)
        email.attach_alternative(html_content, "text/html")
        email.send()
        print(f"Email sent to {to}")
    except Exception as e:
        print(f"Error sending email: {e}")

    
def send_approval_email(reservation):
    subject = "Your Reservation is Approved"
    message = f"Your reservation has been approved.\n\nThank you for choosing us!"
    html_content = f"<p>Hello Dear {reservation.user.first_name} {reservation.user.last_name}<br><br>Your reservation has been approved.<br>Thank you for choosing us!</p>"
    recipient_list = [reservation.user.email]
    # mail_sender(subject, "", html_content, recipient_list)
    mail_sender(subject, "", message, recipient_list)


@receiver(post_save, sender=Reservation)
def update_order_status(sender, instance, **kwargs):
    # The hasattr function checks if an object has a specific attribute.
    # Check if the signal has been processed to avoid infinite loops.
    if not hasattr(instance, "_signal_handled"):
        # Mark the instance to avoid re-processing the signal.
        instance._signal_handled = True
        current_time = timezone.now()
        # Update order status based on conditions.
        if instance.is_approved:
            instance.order_status = "approved"
            if instance.approved_date is None:
                print(f"Sending approval email to {instance.user.email}")
                send_approval_email(instance)
                instance.approved_date = current_time
        elif instance.end_date < current_time:
            print(f"Order {instance.id} marked as expired")
            instance.order_status = "expired"
        else:
            instance.order_status = "pending"
        # Save the instance with updated fields.
        instance.save(update_fields=["order_status"])
        # Remove the temporary attribute.
        del instance._signal_handled


# @receiver(post_save, sender=Reservation)
# def update_order_status(sender, instance, **kwargs):
#     if instance.is_approved:
#         instance.order_status = "approved"
#         if instance.approved_date is None:
#             send_approval_email(instance)
#     elif instance.end_date < timezone.now():
#         instance.order_status = "expired"
#     else:
#         instance.order_status = "pending"
#     Reservation.objects.filter(pk=instance.pk).update(order_status=instance.order_status)


#===========================================================================================================
