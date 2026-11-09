from datetime import datetime
from django.utils import timezone
import pytest
from django.contrib.auth.models import User
from bookings.models import Booking, Table


@pytest.fixture
def booking(db):
    user = User.objects.create_user(username='pytest-user', password='test-pass')
    table = Table.objects.create(table_number='P1', capacity=4)
    return Booking.objects.create(
        user=user,
        table=table,
        booking_datetime=timezone.make_aware(datetime(2030, 1, 1, 19, 0)),
        number_of_guests=2,
        special_requests='pytest fixture',
    )


def test_booking_string_shows_user_and_datetime(booking):
    expected = f'Booking for {booking.user} on {booking.booking_datetime}'

    assert str(booking) == expected


def test_booking_defaults_to_pending(booking):
    assert booking.status == 'pending'
