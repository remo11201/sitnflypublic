from django.test import TestCase
from django.core.mail import send_mail
from django.conf import settings
import logging
import logging
from django.core.mail import send_mail
from django.conf import settings
import os
import sys
import django
logger = logging.getLogger(__name__)
# Add the parent directory (containing sitnfly) to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Create your tests here.
# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sitnfly.settings")
django.setup()


def send_test_email():
    print("Starting send_test_email function")
    logger.debug("Inside send_test_email function")
    subject = 'Test Email'
    message = 'This is a test email from Django.'
    from_email = settings.EMAIL_HOST_USER
    #change recipent to test
    recipient_list = ['jasontky23@gmail.com']

    print(f"Attempting to send email from {from_email} to {recipient_list}")

    try:
        # Send email using Django's send_mail function
        send_mail(subject, message, from_email, recipient_list)
        print("Test email sent successfully!")
    except Exception as e:
        print(f"Error sending test email: {e}")
        logger.exception("Error sending test email")

    print("Finished send_test_email function")

#not working
# from django.conf import settings
# from django.contrib.auth.hashers import get_hasher

# # Print the default password hasher
# print("Default password hasher:", get_hasher().algorithm)

# # Print all configured password hashers
# for hasher_path in settings.PASSWORD_HASHERS:
#     hasher = get_hasher(hasher_path.split('.')[-1])
#     print("Configured password hasher:", hasher.algorithm)


