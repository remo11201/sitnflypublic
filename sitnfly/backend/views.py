from django.shortcuts import render, redirect, get_object_or_404 
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import *
from .forms import MyUserCreationForm, UserForm
# from django_otp import devices_for_user
# from qr_code.qrcode.utils import QRCodeOptions
# from .models import RecoveryCode
from .utils import generate_recovery_codes, validate_recovery_code
# from django_otp.plugins.otp_totp.models import TOTPDevice, TOTP
import random
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from .utils import *
import logging
from django.views.decorators.http import require_POST
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime
from uuid import uuid4
from django.db import transaction

logger = logging.getLogger(__name__)
# Create your views here.
# def payment(request):
#     return render(request, 'payment.html')
# @login_required
# def payment(request):
#     if request.method == "POST":
#         flight_number = request.POST.get('flight_number')
#         origin = request.POST.get('origin')
#         destination = request.POST.get('destination')
#         departure_time = request.POST.get('departure_time')
#         arrival_time = request.POST.get('arrival_time')
#         price = request.POST.get('price')
#         name = request.POST.get('name')
#         email = request.POST.get('email')
#         phone = request.POST.get('phone')

#         context = {
#             'flight_number': flight_number,
#             'origin': origin,
#             'destination': destination,
#             'departure_time': departure_time,
#             'arrival_time': arrival_time,
#             'price': price,
#             'name': name,
#             'email': email,
#             'phone': phone,
#         }
#         return render(request, 'payment.html', context)
#     return render(request, 'payment.html')

@login_required
def payment(request):
    if 'booking' not in request.session:
        return redirect('flight_search')

    # Check if payment has already been processed
    if request.session.get('payment_processed'):
        return redirect('payment_error')  # Redirect to error if payment already processed

    booking_data = request.session.get('booking', None)
    if booking_data is None:
        return redirect('flight_search')

    flight = get_object_or_404(Flight, flight_id=booking_data['flight_id'])
    selected_seats = Seat.objects.filter(pk__in=booking_data['selected_seat_ids'])
    total_price = booking_data['total_price']

    user = request.user

    context = {
        'flight_number': flight.flight_number,
        'origin': flight.origin,
        'destination': flight.destination,
        'departure_time': flight.departure_time,
        'arrival_time': flight.arrival_time,
        'price': total_price,
        'name': user.name,
        'email': user.email,
        'phone': user.phone_number,
    }

    return render(request, 'payment.html', context)

@login_required
def process_payment(request):
    if request.method == 'POST':
        # Generate a unique transaction token
        transaction_token = str(uuid.uuid4())
        
        # Check if transaction token already exists in session to avoid duplicate processing
        if request.session.get('transaction_token') == transaction_token:
            messages.error(request, 'This transaction has already been processed.')
            return redirect('payment_error')

        # Store the transaction token in the session
        request.session['transaction_token'] = transaction_token

        flight_number = request.POST.get('flight_number')
        origin = request.POST.get('origin')
        destination = request.POST.get('destination')
        departure_time = request.POST.get('departure_time')
        arrival_time = request.POST.get('arrival_time')
        price = request.POST.get('price')
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        # Store booking and passenger details in session
        request.session['payment'] = {
            'flight_number': flight_number,
            'origin': origin,
            'destination': destination,
            'departure_time': departure_time,
            'arrival_time': arrival_time,
            'price': price,
            'name': name,
            'email': email,
            'phone': phone,
        }

        try:
            with transaction.atomic():
                # Save reservation and payment to the database
                booking_data = request.session.get('booking')
                flight = get_object_or_404(Flight, flight_id=booking_data['flight_id'])
                user = request.user
                selected_seats = Seat.objects.select_for_update().filter(pk__in=booking_data['selected_seat_ids'])

                for seat in selected_seats:
                    # Check if reservation already exists
                    existing_reservation = Reservation.objects.filter(
                        user=user,
                        flight=flight,
                        seat=seat,
                        reservation_status='Booked'
                    ).exists()

                    if not existing_reservation:
                        reservation = Reservation.objects.create(
                            user=user,
                            flight=flight,
                            seat=seat,
                            reservation_status='Booked',
                            payment_status='Paid'
                        )
                        seat.availability = False
                        seat.save()

                        Payment.objects.create(
                            payment_amount=seat.price,
                            payment_method='Credit/Debit card',  # This should be dynamic based on the user's choice
                            reservation=reservation
                        )

                messages.success(request, 'Your payment has been processed successfully.')
                return redirect('payment_success')
        
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('payment_error')

    return render(request, 'payment.html')

@login_required
def payment_success(request):
    payment_data = request.session.get('payment', {})
    flight_number = payment_data.get('flight_number')
    origin = payment_data.get('origin')
    destination = payment_data.get('destination')
    departure_time = payment_data.get('departure_time')
    arrival_time = payment_data.get('arrival_time')
    price = payment_data.get('price')
    name = payment_data.get('name')
    email = payment_data.get('email')
    phone = payment_data.get('phone')

    context = {
        'flight_number': flight_number,
        'origin': origin,
        'destination': destination,
        'departure_time': departure_time,
        'arrival_time': arrival_time,
        'price': price,
        'name': name,
        'email': email,
        'phone': phone,
    }
    return render(request, 'payment_success.html', context)

@login_required
def payment_error(request):
    return render(request, 'payment_error.html', {'message': 'This transaction has already been processed.'})

def home(request):
    return render(request, 'home.html')


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower().strip()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)

            if not user.is_active:
                # Redirect to 2FA verification page if the account is not active
                request.session['pre_2fa_user_id'] = user.id
                messages.info(request, 'Account is inactive. Please verify your email.')
                return redirect('send_2fa_email')
            
        except User.DoesNotExist:
            messages.error(request, 'User does not exist')
            return render(request, 'login_register.html', {'page': page})
        except Exception as e:
            messages.error(request, f'An unexpected error occurred: {e}')
            return render(request, 'login_register.html', {'page': page})

        user = authenticate(request, email=email, password=password)

        if user is not None:
            if user.is_2fa_enabled:
                # Redirect to 2FA verification page if 2FA is enabled
                request.session['pre_2fa_user_id'] = user.id
                return redirect('send_2fa_email')
            else:
                # Perform login if 2FA is not enabled
                login(request, user)
                
            
                 # Create a new session record using the class method
                SessionLog.create_session(
                    user=user,
                    session_key=request.session.session_key,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:255]
                )
                
                return redirect('home')
        else:
            messages.error(request, 'Username or password is incorrect')

    context = {'page': page}
    return render(request, 'login_register.html', context)

@login_required(login_url='login')
def logoutUser(request):
    # if request.user.is_authenticated:
    session = SessionLog.update_logout(user=request.user, session_key=request.session.session_key)
        
        # if not session:
        #     raise Http404("Session does not exist")  

    logout(request)
    return redirect('home')



def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        # if form.is_valid():
        #     user = form.save(commit=False)
        #     user.email = user.email.lower()
        #     user.save()
        #     login(request, user)
        #     return redirect('home')
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account until 2fa confirmed
            user.save()
            request.session['pre_2fa_user_id'] = user.id
            return redirect('send_2fa_email')
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'login_register.html', {'form': form})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile successfully updated.')
            return redirect('update-user')

    return render(request, 'update-user.html', {'form': form})


    
#  @Jason Original flight_search function, was empty in the web application so I replaced, revert otherwise.
# def flight_search(request):
#     query = request.GET.get('q')
#     flights = Flight.objects.all()  # Retrieve all flights initially

#     if query:
#         # Filter flights based on flight_number, origin, or destination containing the query
#         flights = flights.filter(
#             models.Q(flight_number__icontains=query) |
#             models.Q(origin__icontains=query) |
#             models.Q(destination__icontains=query)
#         )

#     context = {
#         'flights': flights,
#         'query': query
#     }
#     return render(request, 'flight_search.html', context)



# @login_required
# def setup_2fa(request):
#     user = request.user

#     try:
#         # Attempt to get the user's TOTP device
#         device = TOTPDevice.objects.get(user=user)
#     except TOTPDevice.DoesNotExist:
#         # If no TOTP device exists, create one
#         device = TOTPDevice.objects.create(user=user, confirmed=False)

#     if request.method == 'POST':
#         verification_code = request.POST.get('verification_code')
        
#         if device.verify_token(verification_code):
#             device.confirmed = True
#             device.save()
#             messages.success(request, 'Two-Factor Authentication has been successfully set up.')
#             return redirect('dashboard')  # Replace 'dashboard' with your actual dashboard URL name
#         else:
#             messages.error(request, 'Invalid verification code. Please try again.')

#     # Generate provisioning URI and secret key
#     totp = TOTP(device.bin_key)
#     provisioning_uri = totp.provisioning_uri(user.username, issuer_name="YourAppName")

#     context = {
#         'provisioning_uri': provisioning_uri,
#         'secret_key': device.bin_key.decode(),
#     }
#     return render(request, 'setup_2fa.html', context)
@login_required
def setup_2fa_email(request):
    if request.method == 'POST':
        email = request.user.email
        password = request.POST.get('password')
        
        # Authenticate user based on email and password
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            # Toggle 2FA status
            user.is_2fa_enabled = not user.is_2fa_enabled
            user.save()
            
            if user.is_2fa_enabled:
                messages.success(request, 'Two-Factor Authentication has been successfully enabled.')
            else:
                messages.success(request, 'Two-Factor Authentication has been successfully disabled.')
            
            return redirect('update-user')
        else:
            messages.error(request, 'Invalid password. Please try again.')

    return render(request, 'setup_2fa_email.html')


# @login_required
def send_2fa_email(request):
    user_id = request.session.get('pre_2fa_user_id')

    if not user_id:
        messages.error(request, 'User session not found. Please log in again.')
        return redirect('login')

    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        try:
            # Generate a new verification code and send it via email
            new_code = str(random.randint(100000, 999999))
            EmailVerificationCode.objects.create(
                user=user, 
                code=new_code, 
                expiry=timezone.now() + timedelta(minutes=2)
            )
            
            # Send verification email (implement this part in your send_verification_email function)
            send_verification_email(user, new_code)
            
            messages.success(request, 'Verification code sent to your email.')
            return redirect('verify_2fa_email')
        
        except Exception as e:
            messages.error(request, 'An error occurred while sending the verification code. Please try again.')

    return render(request, 'send_2fa_email.html')

# @login_required
def verify_2fa_email(request):
    user_id = request.session.get('pre_2fa_user_id')

    if not user_id:
        messages.error(request, 'User session not found. Please log in again.')
        return redirect('login')

    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        if 'resend_verification_code' in request.POST:
            try:
                messages.success(request, 'Resend Email Verification')
                return redirect('send_2fa_email')
        
            except Exception as e:
                print(f"Error sending verification code: {e}")
                messages.error(request, 'An error occurred while redirecting. Please try again.')

        else:
            code = request.POST.get('verification_code')
            try:
                verification = EmailVerificationCode.objects.get(
                    user=user, 
                    code=code, 
                    used=False,
                    expiry__gt=timezone.now()
                )
                verification.used = True
                verification.save()

                # Activate the user account if it is not already active, redirect to login
                if not user.is_active:
                    user.is_active = True
                    user.save()
                    messages.success(request, 'Registration successful. You can now log in.')
                    return redirect('login')

                # else login
                else:
                    login(request, user)
                    return redirect('home')
            
            except EmailVerificationCode.DoesNotExist:
                messages.error(request, 'Invalid or expired verification code.')

    return render(request, 'verify_2fa_email.html')

# @login_required
# def verify_2fa(request):
#     user = request.user
#     device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
    
#     if not device:
#         return redirect('setup_2fa')
    
#     if request.method == 'POST':
#         verification_code = request.POST.get('verification_code')
#         if device.verify_token(verification_code):
#             # Mark the user as verified for this session
#             request.session['2fa_verified'] = True
#             return redirect('dashboard')  # Replace with your dashboard URL name
#         else:
#             messages.error(request, 'Invalid verification code. Please try again.')
    
#     return render(request, 'verify_2fa.html')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')





@login_required(login_url='login')
def manage_bookings(request):
    user = request.user
    reservations = Reservation.objects.filter(user=user).select_related('flight', 'seat')

    booking_details = []
    for reservation in reservations:
        flight = reservation.flight
        seat = reservation.seat
        booking_details.append({
            'flight_number': flight.flight_number,
            'departure_time': flight.departure_time,
            'arrival_time': flight.arrival_time,
            'origin': flight.origin,
            'destination': flight.destination,
            'airline_name': flight.airline_name,
            'seat_number': seat.seat_no,
            'seat_class': seat.seat_class,
            'reservation_status': reservation.reservation_status,
            'payment_status': reservation.payment_status,
            'booking_date': reservation.booking_date,
        })

    context = {
        'booking_details': booking_details,
    }
    return render(request, 'manage_bookings.html', context)


from datetime import datetime

def flight_search(request):
    origins = Flight.objects.values_list('origin', flat=True).distinct()
    destinations = Flight.objects.values_list('destination', flat=True).distinct()

    if request.method == 'GET':
        origin = request.GET.get('origin')
        destination = request.GET.get('destination')
        depart_date_str = request.GET.get('depart_date')
        return_date_str = request.GET.get('return_date')
        seat_class = request.GET.get('seat_class')

        # Check if origin and destination are provided
        if not origin or not destination:
            context = {
                'origins': origins,
                'destinations': destinations,
                'error_message': 'Origin and Destination are required.',
            }
            return render(request, 'flight_search.html', context)

        # Validate depart_date and return_date
        try:
            if depart_date_str:
                depart_date = datetime.strptime(depart_date_str, '%Y-%m-%d').date()
                if depart_date < timezone.now().date():
                    raise ValidationError('Departure date cannot be in the past.')
            else:
                depart_date = None

            if return_date_str:
                return_date = datetime.strptime(return_date_str, '%Y-%m-%d').date()
                if return_date < depart_date:
                    raise ValidationError('Return date cannot be before departure date.')
            else:
                return_date = None

        except ValueError:
            context = {
                'origins': origins,
                'destinations': destinations,
                'error_message': 'Invalid date format.',
            }
            return render(request, 'flight_search.html', context)
        except ValidationError as e:
            context = {
                'origins': origins,
                'destinations': destinations,
                'error_message': str(e),
            }
            return render(request, 'flight_search.html', context)

        # Filter flights based on provided parameters
        flights = Flight.objects.filter(
            origin=origin,
            destination=destination,
        )

        if depart_date:
            flights = flights.filter(departure_time__date=depart_date)

        if return_date:
            flights = flights.filter(arrival_time__date=return_date)

        # Filter flights based on seat_class (join like)
        if seat_class:
            seat_ids = Seat.objects.filter(seat_class=seat_class).values_list('flight_id', flat=True)
            flights = flights.filter(flight_id__in=seat_ids)

        # Check if any flights match the criteria
        if not flights.exists():
            context = {
                'origins': origins,
                'destinations': destinations,
                'error_message': 'No flights found matching your criteria.',
            }
            return render(request, 'flight_search.html', context)

        context = {
            'origins': origins,
            'destinations': destinations,
            'flights': flights,
            'origin': origin,
            'destination': destination,
            'depart_date': depart_date_str,
            'return_date': return_date_str,
            'seat_class': seat_class,
        }

    return render(request, 'flight_search.html', context)


@login_required(login_url='login')
def flight_booking(request, flight_id):
    flight = get_object_or_404(Flight, flight_id=flight_id)
    available_seats = Seat.objects.filter(flight_id=flight_id, availability=True)
    
    if request.method == 'POST':
        selected_seat_ids = request.POST.getlist('seat_ids')
        selected_seats = Seat.objects.filter(pk__in=selected_seat_ids)
        
        total_price = sum(seat.price for seat in selected_seats)
        
        # Convert total_price to float or string before storing in session
        total_price_str = str(total_price)  # Convert to string
        
        booking_id = str(uuid4())
        
        # Store booking details in session
        request.session['booking'] = {
            'booking_id': booking_id,
            'flight_id': flight_id,
            'selected_seat_ids': selected_seat_ids,
            'total_price': total_price_str,  # Store as string
        }
        
        return redirect(reverse('booking_confirmation', kwargs={'booking_id': booking_id}))
    
    context = {
        'flight': flight,
        'available_seats': available_seats,
    }
    return render(request, 'flight_booking.html', context)

@login_required(login_url='login')
def booking_confirmation(request, booking_id):
    if 'booking' not in request.session or request.session['booking']['booking_id'] != booking_id:
        # Redirect to flight search or handle error
        return redirect('flight_search')
    
    booking_data = request.session['booking']
    flight = get_object_or_404(Flight, flight_id=booking_data['flight_id'])
    selected_seats = Seat.objects.filter(pk__in=booking_data['selected_seat_ids'])
    total_price = booking_data['total_price']
    
    context = {
        'flight': flight,
        'selected_seats': selected_seats,
        'total_price': total_price,
    }
    return render(request, 'flight_booking_confirmation.html', context)
