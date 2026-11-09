from datetime import timedelta

from django.test import SimpleTestCase
from django.utils import timezone
from website.forms import BookingForm


class TestBookingForm(SimpleTestCase):
    def make_form(self, booking_date):
        return BookingForm(data={
            'booking_date': booking_date.isoformat(),
            'booking_time': '19:00',
            'number_of_guests': 2,
            'special_requests': '',
        })

    def test_form_missing_required_fields(self):
        form = BookingForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('booking_date', form.errors)
        self.assertIn('booking_time', form.errors)
        self.assertIn('number_of_guests', form.errors)

    def test_past_booking_date_is_rejected(self):
        past_date = timezone.localdate() - timedelta(days=1)

        form = self.make_form(past_date)

        self.assertFalse(form.is_valid())
        self.assertIn(
            'Booking must be in the future.',
            form.errors['booking_date'],
        )

    def test_bookable_future_date_is_accepted(self):
        future_date = timezone.localdate() + timedelta(days=1)

        form = self.make_form(future_date)

        self.assertTrue(form.is_valid(), form.errors)
        booking_datetime = form.cleaned_data['booking_datetime']
        self.assertTrue(timezone.is_aware(booking_datetime))
        self.assertGreater(booking_datetime, timezone.now())
