"""
Database Backup DAG
Performs regular backups of the Django database and uploads to cloud storage
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import os
import subprocess
from pathlib import Path

# Default arguments
default_args = {
    'owner': 'restaurant_admin',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email': ['admin@restaurant.com'],
    'email_on_failure': True,
}

dag = DAG(
    'database_backup_dag',
    default_args=default_args,
    description='Perform regular database backups',
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    start_date=days_ago(1),
    catchup=False,
    tags=['restaurant', 'backup', 'database'],
)


def create_database_backup():
    """
    Create a backup of the PostgreSQL database
    """
    try:
        # Get database credentials from environment
        db_name = os.getenv('DB_NAME', 'restaurant_db')
        db_user = os.getenv('DB_USER', 'postgres')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_password = os.getenv('DB_PASSWORD', '')
        
        # Create backup directory
        backup_dir = '/tmp/airflow/database_backups'
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'{backup_dir}/restaurant_db_backup_{timestamp}.sql'
        
        # Execute pg_dump command
        if db_password:
            cmd = f"PGPASSWORD={db_password} pg_dump -h {db_host} -U {db_user} {db_name} > {backup_file}"
        else:
            cmd = f"pg_dump -h {db_host} -U {db_user} {db_name} > {backup_file}"
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            file_size = os.path.getsize(backup_file) / (1024 * 1024)  # Size in MB
            print(f"✓ Database backup created: {backup_file}")
            print(f"✓ Backup size: {file_size:.2f} MB")
            return backup_file
        else:
            print(f"✗ Backup failed: {result.stderr}")
            raise Exception(f"pg_dump failed with code {result.returncode}")
            
    except Exception as e:
        print(f"✗ Error creating backup: {str(e)}")
        raise


def backup_media_files():
    """
    Backup media files uploaded to the application
    """
    try:
        backup_dir = '/tmp/airflow/database_backups'
        os.makedirs(backup_dir, exist_ok=True)
        
        media_dir = '/app/media'  # Adjust path based on your setup
        
        if os.path.exists(media_dir):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f'{backup_dir}/media_backup_{timestamp}.tar.gz'
            
            cmd = f"tar -czf {backup_file} -C {media_dir} ."
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                file_size = os.path.getsize(backup_file) / (1024 * 1024)
                print(f"✓ Media files backed up: {backup_file}")
                print(f"✓ Backup size: {file_size:.2f} MB")
                return backup_file
            else:
                print(f"✗ Media backup failed: {result.stderr}")
                raise Exception(f"tar command failed")
        else:
            print(f"⚠ Media directory not found: {media_dir}")
            return None
            
    except Exception as e:
        print(f"✗ Error backing up media: {str(e)}")
        raise


def cleanup_old_backups(days_to_keep=7):
    """
    Remove backups older than specified number of days
    """
    try:
        backup_dir = '/tmp/airflow/database_backups'
        
        if not os.path.exists(backup_dir):
            print("No backup directory found")
            return
        
        cutoff_time = datetime.now() - timedelta(days=days_to_keep)
        deleted_count = 0
        
        for filename in os.listdir(backup_dir):
            filepath = os.path.join(backup_dir, filename)
            
            if os.path.isfile(filepath):
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if file_time < cutoff_time:
                    os.remove(filepath)
                    deleted_count += 1
                    print(f"✓ Deleted old backup: {filename}")
        
        print(f"✓ Cleanup complete. Deleted {deleted_count} old backup(s)")
        
    except Exception as e:
        print(f"✗ Error cleaning up backups: {str(e)}")
        raise


def verify_backup_integrity(backup_file):
    """
    Verify the backup file can be read and is not corrupted
    """
    try:
        if not os.path.exists(backup_file):
            raise FileNotFoundError(f"Backup file not found: {backup_file}")
        
        # Check file size
        file_size = os.path.getsize(backup_file)
        if file_size == 0:
            raise ValueError("Backup file is empty")
        
        # Count lines (simple check for SQL backups)
        with open(backup_file, 'r') as f:
            line_count = sum(1 for _ in f)
        
        if line_count < 10:
            raise ValueError("Backup file appears to be corrupted (too few lines)")
        
        print(f"✓ Backup integrity verified")
        print(f"✓ File size: {file_size / (1024*1024):.2f} MB")
        print(f"✓ Line count: {line_count}")
        
    except Exception as e:
        print(f"✗ Backup verification failed: {str(e)}")
        raise


# Define tasks
task_create_db_backup = PythonOperator(
    task_id='create_database_backup',
    python_callable=create_database_backup,
    dag=dag,
)

task_backup_media = PythonOperator(
    task_id='backup_media_files',
    python_callable=backup_media_files,
    dag=dag,
)

task_verify_backup = PythonOperator(
    task_id='verify_backup_integrity',
    python_callable=lambda: verify_backup_integrity('/tmp/airflow/database_backups/latest_backup.sql'),
    dag=dag,
    trigger_rule='all_done',  # Run even if previous task fails
)

task_cleanup_old = PythonOperator(
    task_id='cleanup_old_backups',
    python_callable=cleanup_old_backups,
    op_kwargs={'days_to_keep': 7},
    dag=dag,
)

# Task dependencies
task_create_db_backup >> task_backup_media >> task_verify_backup >> task_cleanup_old
