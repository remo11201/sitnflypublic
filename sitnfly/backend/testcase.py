from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from datetime import datetime, timedelta
from .models import Flight, User, Payment, Reservation, EmailVerificationCode, Seat

class FlightSearchViewTestCase(TestCase):
    def test_flight_search_valid(self):
        url = reverse('flight_search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'flight_search.html')

        # Test with valid data
        data = {
            'origin': 'New York',
            'destination': 'Los Angeles',
            'depart_date': datetime.now().strftime('%Y-%m-%d'),
            'return_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'seat_class': 'Economy',
        }
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('flights', response.context)
        self.assertGreater(len(response.context['flights']), 0)

    def test_flight_search_invalid(self):
        url = reverse('flight_search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'flight_search.html')

        # Test with invalid data
        data = {
            'origin': '',
            'destination': 'Los Angeles',
            'depart_date': datetime.now().strftime('%Y-%m-%d'),
            'return_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'seat_class': 'Economy',
        }
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('error_message', response.context)
        self.assertEqual(response.context['error_message'], 'Origin and Destination are required.')

class PaymentViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password')
        self.client.force_login(self.user)
        self.flight = Flight.objects.create(flight_number='ABC123', origin='New York', destination='Los Angeles',
                                            departure_time=datetime.now(), arrival_time=datetime.now())
        self.seat = Seat.objects.create(seat_no='A1', seat_class='Economy', availability=True, flight=self.flight,
                                        price=100)
        self.booking_data = {
            'flight_id': self.flight.id,
            'selected_seat_ids': [self.seat.id],
            'total_price': 100,
        }

    def test_payment_authenticated_user(self):
        url = reverse('payment')
        self.client.session['booking'] = self.booking_data
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment.html')

    def test_payment_unauthenticated_user_redirect(self):
        self.client.logout()
        url = reverse('payment')
        self.client.session['booking'] = self.booking_data
        response = self.client.get(url)
        self.assertRedirects(response, '/accounts/login/?next=/payment/')

    def test_payment_processed_redirect(self):
        url = reverse('payment')
        self.client.session['booking'] = self.booking_data
        self.client.session['payment_processed'] = True
        response = self.client.get(url)
        self.assertRedirects(response, '/payment_error/')


class ProcessPaymentViewTestCase(TransactionTestCase):  # Use TransactionTestCase for explicit transaction control
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password')
        self.client.force_login(self.user)
        self.flight = Flight.objects.create(flight_number='ABC123', origin='New York', destination='Los Angeles',
                                            departure_time=datetime.now(), arrival_time=datetime.now())
        self.seat = Seat.objects.create(seat_no='A1', seat_class='Economy', availability=True, flight=self.flight,
                                        price=100)
        self.booking_data = {
            'flight_id': self.flight.id,
            'selected_seat_ids': [self.seat.id],
            'total_price': 100,
        }

    def test_process_payment_post(self):
        url = reverse('process_payment')
        self.client.session['booking'] = self.booking_data
        response = self.client.post(url, {
            'flight_number': 'ABC123',
            'origin': 'New York',
            'destination': 'Los Angeles',
            'departure_time': self.flight.departure_time,
            'arrival_time': self.flight.arrival_time,
            'price': 100,
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '1234567890',
        })
        self.assertRedirects(response, '/payment_success/')
        self.assertTrue(Reservation.objects.filter(user=self.user, flight=self.flight, seat=self.seat).exists())
        self.assertTrue(Payment.objects.filter(reservation__user=self.user).exists())

    def test_process_payment_duplicate_transaction_token(self):
        url = reverse('process_payment')
        self.client.session['booking'] = self.booking_data
        self.client.session['transaction_token'] = 'test_token'
        response = self.client.post(url, {
            'flight_number': 'ABC123',
            'origin': 'New York',
            'destination': 'Los Angeles',
            'departure_time': self.flight.departure_time,
            'arrival_time': self.flight.arrival_time,
            'price': 100,
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '1234567890',
        })
        self.assertRedirects(response, '/payment_error/')
        self.assertIn('This transaction has already been processed.', response.context['message'])

class Setup2FAEmailViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password')
        self.client.force_login(self.user)

    def test_setup_2fa_email_post(self):
        url = reverse('setup_2fa_email')
        response = self.client.post(url, {
            'password': 'password',
        })
        self.assertRedirects(response, '/update-user/')
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_2fa_enabled)

    def test_setup_2fa_email_invalid_password(self):
        url = reverse('setup_2fa_email')
        response = self.client.post(url, {
            'password': 'wrong_password',
        })
        self.assertTemplateUsed(response, 'setup_2fa_email.html')
        self.assertFalse(self.user.is_2fa_enabled)


class Send2FAEmailViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password')
        self.client.force_login(self.user)

    def test_send_2fa_email_post(self):
        url = reverse('send_2fa_email')
        response = self.client.post(url)
        self.assertRedirects(response, '/verify_2fa_email/')
        self.assertTrue(EmailVerificationCode.objects.filter(user=self.user).exists())

class Verify2FAEmailViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password')
        self.client.force_login(self.user)
        self.verification_code = '123456'
        EmailVerificationCode.objects.create(user=self.user, code=self.verification_code)

    def test_verify_2fa_email_post_correct_code(self):
        url = reverse('verify_2fa_email')
        response = self.client.post(url, {
            'verification_code': self.verification_code,
        })
        self.assertRedirects(response, '/home/')
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_verify_2fa_email_post_incorrect_code(self):
        url = reverse('verify_2fa_email')
        response = self.client.post(url, {
            'verification_code': '654321',
        })
        self.assertTemplateUsed(response, 'verify_2fa_email.html')
        self.assertFalse(self.user.is_active)
