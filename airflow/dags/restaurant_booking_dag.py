"""
Restaurant Booking Management DAG
Handles automated tasks for restaurant reservation system
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_booking.settings')
django.setup()

from bookings.models import Booking

# Default arguments for the DAG
default_args = {
    'owner': 'restaurant_admin',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email': ['admin@restaurant.com'],
    'email_on_failure': True,
    'email_on_retry': False,
}

# DAG definition
dag = DAG(
    'restaurant_booking_dag',
    default_args=default_args,
    description='Automated restaurant booking management tasks',
    schedule_interval='0 * * * *',  # Every hour
    start_date=days_ago(1),
    catchup=False,
    tags=['restaurant', 'bookings'],
)


# Task 1: Auto-confirm pending bookings (older than 24 hours)
def confirm_old_pending_bookings():
    """
    Automatically confirm pending bookings that are older than 24 hours
    """
    try:
        now = datetime.now()
        cutoff_time = now - timedelta(hours=24)
        
        old_pending = Booking.objects.filter(
            status='pending',
            booking_datetime__lt=cutoff_time
        )
        
        count = old_pending.count()
        if count > 0:
            old_pending.update(status='confirmed')
            print(f"✓ Auto-confirmed {count} pending bookings")
        else:
            print("No pending bookings to confirm")
            
    except Exception as e:
        print(f"✗ Error confirming bookings: {str(e)}")
        raise


# Task 2: Cancel no-show bookings
def cancel_past_bookings():
    """
    Cancel bookings that have passed their booking time without confirmation
    """
    try:
        now = datetime.now()
        past_pending = Booking.objects.filter(
            status='pending',
            booking_datetime__lt=now
        )
        
        count = past_pending.count()
        if count > 0:
            past_pending.update(status='cancelled')
            print(f"✓ Cancelled {count} past pending bookings")
        else:
            print("No past bookings to cancel")
            
    except Exception as e:
        print(f"✗ Error cancelling bookings: {str(e)}")
        raise


# Task 3: Generate booking summary report
def generate_booking_report():
    """
    Generate daily booking summary report
    """
    try:
        today = datetime.now().date()
        bookings_today = Booking.objects.filter(
            booking_datetime__date=today
        )
        
        summary = {
            'total_bookings': bookings_today.count(),
            'pending': bookings_today.filter(status='pending').count(),
            'confirmed': bookings_today.filter(status='confirmed').count(),
            'rejected': bookings_today.filter(status='rejected').count(),
            'cancelled': bookings_today.filter(status='cancelled').count(),
            'total_guests': sum(b.number_of_guests for b in bookings_today),
        }
        
        report = f"""
        === BOOKING REPORT FOR {today} ===
        Total Bookings: {summary['total_bookings']}
        - Pending: {summary['pending']}
        - Confirmed: {summary['confirmed']}
        - Rejected: {summary['rejected']}
        - Cancelled: {summary['cancelled']}
        Total Guests Expected: {summary['total_guests']}
        ================================
        """
        
        print(report)
        
        # Save report to file
        log_dir = '/tmp/airflow/booking_reports'
        os.makedirs(log_dir, exist_ok=True)
        
        with open(f'{log_dir}/report_{today}.txt', 'w') as f:
            f.write(report)
            
        print(f"✓ Report saved to {log_dir}/report_{today}.txt")
        
    except Exception as e:
        print(f"✗ Error generating report: {str(e)}")
        raise


# Task 4: Check table availability
def check_table_availability():
    """
    Log current table availability status
    """
    try:
        from bookings.models import Table
        
        all_tables = Table.objects.all()
        confirmed_bookings = Booking.objects.filter(
            status='confirmed',
            booking_datetime__gte=datetime.now()
        ).values_list('table_id', flat=True)
        
        available = []
        occupied = []
        
        for table in all_tables:
            if table.id in confirmed_bookings:
                occupied.append(f"Table {table.table_number}")
            else:
                available.append(f"Table {table.table_number}")
        
        availability_report = f"""
        === TABLE AVAILABILITY STATUS ===
        Available: {len(available)} tables
        {', '.join(available) if available else 'None'}
        
        Occupied: {len(occupied)} tables
        {', '.join(occupied) if occupied else 'None'}
        ===================================
        """
        
        print(availability_report)
        
    except Exception as e:
        print(f"✗ Error checking availability: {str(e)}")
        raise


# Define DAG tasks
task_1 = PythonOperator(
    task_id='confirm_pending_bookings',
    python_callable=confirm_old_pending_bookings,
    dag=dag,
)

task_2 = PythonOperator(
    task_id='cancel_past_bookings',
    python_callable=cancel_past_bookings,
    dag=dag,
)

task_3 = PythonOperator(
    task_id='generate_booking_report',
    python_callable=generate_booking_report,
    dag=dag,
)

task_4 = PythonOperator(
    task_id='check_table_availability',
    python_callable=check_table_availability,
    dag=dag,
)

# Set task dependencies
task_1 >> task_2 >> [task_3, task_4]
