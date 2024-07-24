from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, null=True)
    name = models.CharField(max_length=255, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    role = models.CharField(max_length=20, choices=[('Customer', 'Customer'), ('Administrator', 'Administrator')], default='Customer')
    is_2fa_enabled = models.BooleanField(default=False)  
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
class SessionLog(models.Model):
    session_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, default='')  
    ip_address = models.GenericIPAddressField(default='0.0.0.0')  
    user_agent = models.CharField(max_length=255, default='NIL')  
    login_time = models.DateTimeField(auto_now_add=True)  
    logout_time = models.DateTimeField(null=True, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)  
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return f"Login session {self.session_id} for {self.user.email}"
    
    @classmethod
    def create_session(cls, user, session_key, ip_address, user_agent):
        current_time = timezone.now()
        return cls.objects.create(
            user=user,
            session_key=session_key,
            ip_address=ip_address,
            user_agent=user_agent[:255],
            login_time=current_time,
            created_at=current_time
        )

    @classmethod
    def update_logout(cls, user, session_key):
        try:
            session = cls.objects.get(
                user=user,
                session_key=session_key,
                is_active=True
            )
            current_time = timezone.now()
            session.logout_time = current_time
            session.is_active = False
            session.save()
        except cls.DoesNotExist:
            # Handle the case where the session record doesn't exist
            pass

class Seat(models.Model):
    seat_id = models.AutoField(primary_key=True)
    seat_no = models.CharField(max_length=255)
    seat_class = models.CharField(max_length=20, choices=[('Economy', 'Economy'),('Business', 'Business'),('First', 'First')])
    availability = models.BooleanField(default=True)
    flight = models.ForeignKey('Flight', on_delete=models.CASCADE, related_name='seats')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    reservation = models.ForeignKey('Reservation', on_delete=models.SET_NULL, null=True, blank=True, related_name='seats')

    def __str__(self):
        return f'{self.seat_no} - {self.seat_class}'
    
class Flight(models.Model):
    flight_id = models.CharField(primary_key=True, max_length=255)
    flight_number = models.CharField(max_length=255)
    departure_time = models.DateTimeField(null=True)
    arrival_time = models.DateTimeField(null=True)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    airline_name= models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"Flight {self.flight_number} from {self.origin} to {self.destination}"
    
class Reservation(models.Model):
    reservation_id = models.AutoField(primary_key=True)
    reservation_status = models.CharField(max_length=20, choices=[('Booked', 'Booked'), ('Rescheduled', 'Rescheduled'), ('Cancelled', 'Cancelled')])
    booking_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')])
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='reservations')
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name='reservations')

    def __str__(self):
        return f"Reservation {self.reservation_id} for {self.user.email}"

class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)

    def __str__(self):
        return f"Payment {self.payment_id} for Reservation {self.reservation.reservation_id}"
    

class RecoveryCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=36, unique=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {'Used' if self.used else 'Unused'}"

class EmailVerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    expiry = models.DateTimeField()
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"Verification Code {self.code} for {self.user.username}"

    def is_expired(self):
        return timezone.now() >= self.expiry
    