"""
Booking Notifications DAG
Sends automated email notifications to users about their bookings
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import os
import django
from django.core.mail import send_mail

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_booking.settings')
django.setup()

from bookings.models import Booking
from django.contrib.auth.models import User

# Default arguments
default_args = {
    'owner': 'restaurant_admin',
    'retries': 2,
    'retry_delay': timedelta(minutes=10),
    'email': ['admin@restaurant.com'],
    'email_on_failure': True,
}

dag = DAG(
    'booking_notifications_dag',
    default_args=default_args,
    description='Send automated booking notifications to users',
    schedule_interval='0 9,17 * * *',  # 9 AM and 5 PM daily
    start_date=days_ago(1),
    catchup=False,
    tags=['restaurant', 'notifications', 'email'],
)


def send_upcoming_booking_reminders():
    """
    Send reminder emails for bookings in the next 24 hours
    """
    try:
        now = datetime.now()
        tomorrow = now + timedelta(hours=24)
        
        upcoming_bookings = Booking.objects.filter(
            status='confirmed',
            booking_datetime__gte=now,
            booking_datetime__lte=tomorrow
        )
        
        reminder_count = 0
        for booking in upcoming_bookings:
            user = booking.user
            subject = f"Reminder: Your Restaurant Booking on {booking.booking_datetime.strftime('%Y-%m-%d %H:%M')}"
            
            message = f"""
Hello {user.first_name or user.username},

This is a friendly reminder about your upcoming reservation.

Booking Details:
- Date & Time: {booking.booking_datetime.strftime('%Y-%m-%d %H:%M')}
- Number of Guests: {booking.number_of_guests}
- Table: {booking.table.table_number if booking.table else 'To be assigned'}
- Special Requests: {booking.special_requests or 'None'}

Please arrive 10 minutes early. If you need to cancel or modify your booking, 
please let us know as soon as possible.

Thank you for choosing our restaurant!

Best regards,
Restaurant Management Team
            """
            
            try:
                send_mail(
                    subject,
                    message,
                    'noreply@restaurant.com',
                    [user.email],
                    fail_silently=False,
                )
                reminder_count += 1
            except Exception as e:
                print(f"✗ Failed to send reminder to {user.email}: {str(e)}")
        
        print(f"✓ Sent {reminder_count} reminder emails")
        
    except Exception as e:
        print(f"✗ Error sending reminders: {str(e)}")
        raise


def send_confirmation_emails():
    """
    Send confirmation emails for recently confirmed bookings
    """
    try:
        recent_time = datetime.now() - timedelta(hours=1)
        
        # This assumes you have a created_at or confirmed_at field
        # Adjust based on your actual Booking model
        recent_confirmations = Booking.objects.filter(
            status='confirmed'
        )[:10]  # Send to recently confirmed bookings
        
        confirmation_count = 0
        for booking in recent_confirmations:
            user = booking.user
            subject = f"Booking Confirmation - {booking.booking_datetime.strftime('%Y-%m-%d')}"
            
            message = f"""
Hello {user.first_name or user.username},

Your booking has been confirmed! 

Booking Details:
- Date & Time: {booking.booking_datetime.strftime('%Y-%m-%d %H:%M')}
- Number of Guests: {booking.number_of_guests}
- Table: {booking.table.table_number if booking.table else 'To be assigned'}
- Confirmation Number: BK{booking.id:06d}

Please keep this email for your records. If you have any questions, 
feel free to contact us.

Thank you!
            """
            
            try:
                send_mail(
                    subject,
                    message,
                    'noreply@restaurant.com',
                    [user.email],
                    fail_silently=False,
                )
                confirmation_count += 1
            except Exception as e:
                print(f"✗ Failed to send confirmation to {user.email}: {str(e)}")
        
        print(f"✓ Sent {confirmation_count} confirmation emails")
        
    except Exception as e:
        print(f"✗ Error sending confirmations: {str(e)}")
        raise


def send_cancellation_notices():
    """
    Send notifications for cancelled bookings
    """
    try:
        cancelled_bookings = Booking.objects.filter(
            status='cancelled'
        )[:5]  # Get recently cancelled
        
        notice_count = 0
        for booking in cancelled_bookings:
            user = booking.user
            subject = "Your Booking Has Been Cancelled"
            
            message = f"""
Hello {user.first_name or user.username},

We regret to inform you that the following booking has been cancelled:

Booking Details:
- Date & Time: {booking.booking_datetime.strftime('%Y-%m-%d %H:%M')}
- Number of Guests: {booking.number_of_guests}
- Confirmation Number: BK{booking.id:06d}

If you would like to make a new reservation, please visit our website.

We look forward to seeing you soon!
            """
            
            try:
                send_mail(
                    subject,
                    message,
                    'noreply@restaurant.com',
                    [user.email],
                    fail_silently=False,
                )
                notice_count += 1
            except Exception as e:
                print(f"✗ Failed to send cancellation notice to {user.email}: {str(e)}")
        
        print(f"✓ Sent {notice_count} cancellation notices")
        
    except Exception as e:
        print(f"✗ Error sending cancellation notices: {str(e)}")
        raise


# Define tasks
task_reminders = PythonOperator(
    task_id='send_booking_reminders',
    python_callable=send_upcoming_booking_reminders,
    dag=dag,
)

task_confirmations = PythonOperator(
    task_id='send_confirmation_emails',
    python_callable=send_confirmation_emails,
    dag=dag,
)

task_cancellations = PythonOperator(
    task_id='send_cancellation_notices',
    python_callable=send_cancellation_notices,
    dag=dag,
)

# Task dependencies
task_reminders >> task_confirmations >> task_cancellations
