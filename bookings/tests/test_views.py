from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from bookings.models import Booking, Table
from datetime import datetime, timedelta
from django.utils import timezone

class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.table = Table.objects.create(table_number='A1', capacity=4)
        self.booking = Booking.objects.create(
            user=self.user,
            table=self.table,
            booking_datetime=timezone.make_aware(datetime(2030, 1, 1, 19, 0)),
            number_of_guests=2,
            status='pending',
            special_requests='Test view'
        )

    def test_profile_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, '/accounts/login/?next=/profile/')

    def test_profile_logged_in(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    def booking_form_data(self, booking_date):
        return {
            'booking_date': booking_date.isoformat(),
            'booking_time': '19:00',
            'number_of_guests': 2,
            'special_requests': 'Integration test',
        }

    def test_create_booking_rejects_past_date_without_saving(self):
        self.client.force_login(self.user)
        existing_count = Booking.objects.filter(user=self.user).count()
        past_date = timezone.localdate() - timedelta(days=1)

        response = self.client.post(
            reverse('create_booking'),
            data=self.booking_form_data(past_date),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Booking must be in the future.')
        self.assertEqual(
            Booking.objects.filter(user=self.user).count(),
            existing_count,
        )

    def test_create_booking_saves_bookable_future_date(self):
        self.client.force_login(self.user)
        future_date = timezone.localdate() + timedelta(days=1)

        response = self.client.post(
            reverse('create_booking'),
            data=self.booking_form_data(future_date),
        )

        self.assertRedirects(response, reverse('booking_list'))
        booking = Booking.objects.filter(
            user=self.user,
            special_requests='Integration test',
        ).latest('pk')
        self.assertGreater(booking.booking_datetime, timezone.now())
