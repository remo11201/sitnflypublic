import uuid
from .models import RecoveryCode
from django.core.mail import send_mail
from django.conf import settings
def generate_recovery_codes(user, num_codes=10):
    codes = []
    for _ in range(num_codes):
        code = str(uuid.uuid4())
        RecoveryCode.objects.create(user=user, code=code)
        codes.append(code)
    return codes

def validate_recovery_code(user, code):
    try:
        recovery_code = RecoveryCode.objects.get(user=user, code=code, used=False)
        recovery_code.used = True
        recovery_code.save()
        return True
    except RecoveryCode.DoesNotExist:
        return False

def send_verification_email(user, code):
    if hasattr(user, 'email'):
        subject = 'Your Verification Code'
        message = f'Hi {user.name},\n\nYour verification code is {code}. It expires in 2 minutes.\n\nThank you!'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user.email]
        
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    else:
        raise ValueError('Invalid user object passed to send_verification_email: missing email attribute')