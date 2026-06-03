# Apache Airflow Setup for Restaurant Booking Application

This directory contains Apache Airflow DAGs and configuration files for automating restaurant booking management tasks.

## 📋 Overview

Apache Airflow is a workflow orchestration platform that helps automate recurring tasks in your restaurant booking application. This setup includes three main DAGs:

### 1. **Restaurant Booking DAG** (`restaurant_booking_dag.py`)
Manages daily booking operations:
- ✅ Auto-confirm pending bookings older than 24 hours
- ❌ Cancel past bookings that haven't been confirmed
- 📊 Generate daily booking reports
- 📍 Check table availability status

**Schedule:** Runs every hour

### 2. **Booking Notifications DAG** (`booking_notifications_dag.py`)
Sends automated email notifications:
- 🔔 Reminder emails for upcoming bookings (24 hours before)
- ✉️ Confirmation emails for newly confirmed bookings
- 📬 Cancellation notices for cancelled bookings

**Schedule:** Runs at 9 AM and 5 PM daily

### 3. **Database Backup DAG** (`data_backup_dag.py`)
Performs regular database maintenance:
- 💾 Create PostgreSQL database backups
- 📦 Backup media and uploaded files
- ✔️ Verify backup integrity
- 🧹 Clean up old backups (older than 7 days)

**Schedule:** Runs daily at 2 AM

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Django project (already configured in your repository)
- PostgreSQL (for backup functionality)

### Installation

1. **Install Apache Airflow:**
   ```bash
   pip install apache-airflow==2.8.1
   ```

2. **Run the setup script:**
   ```bash
   chmod +x airflow/setup_airflow.sh
   ./airflow/setup_airflow.sh
   ```

   Or manually:
   ```bash
   export AIRFLOW_HOME=~/airflow
   airflow db init
   airflow users create --role Admin --username admin --email admin@example.com --firstname Admin --lastname User --password password123
   ```

3. **Copy DAGs to Airflow:**
   ```bash
   cp airflow/dags/*.py ~/airflow/dags/
   ```

### Running Airflow

**Start the Webserver** (in one terminal):
```bash
airflow webserver --port 8080
```

**Start the Scheduler** (in another terminal):
```bash
export DJANGO_SETTINGS_MODULE=restaurant_booking.settings
airflow scheduler
```

**Access the UI:**
- Open http://localhost:8080 in your browser
- Login with your admin credentials

## 📝 Configuration

### Email Configuration
For email notifications to work, configure SMTP settings in `~/.airflow/airflow.cfg`:

```ini
[email]
email_backend = airflow.providers.email.backends.smtp.SendEmailBackend

[smtp]
smtp_host = your-smtp-server.com
smtp_port = 587
smtp_user = your-email@example.com
smtp_password = your-password
smtp_mail_from = noreply@restaurant.com
```

### Database Configuration
Ensure your Django database credentials are set in environment variables:

```bash
export DB_NAME=restaurant_db
export DB_USER=postgres
export DB_PASSWORD=your_password
export DB_HOST=localhost
```

### Django Integration
Make sure `DJANGO_SETTINGS_MODULE` is set:

```bash
export DJANGO_SETTINGS_MODULE=restaurant_booking.settings
```

## 🔍 Monitoring DAGs

### View DAG Status
In the Airflow UI, you can:
- View all DAGs and their schedules
- Trigger DAGs manually
- Check task execution history
- View logs for each task

### Task Failures
If a task fails:
1. Check the logs in the UI (click on the task → Log)
2. Verify environment variables and configurations
3. Check Django settings and database connectivity
4. Review error messages in `/~/airflow/logs/`

## 🛠️ Customization

### Modifying Task Schedules
Edit the `schedule_interval` parameter in each DAG:

```python
dag = DAG(
    'my_dag',
    schedule_interval='0 9 * * *',  # 9 AM daily
    # ... other parameters
)
```

Common schedule patterns:
- `'0 * * * *'` - Every hour
- `'0 9 * * *'` - 9 AM daily
- `'0 9 * * MON'` - 9 AM every Monday
- `'*/30 * * * *'` - Every 30 minutes

### Adding Custom Tasks
Create a new DAG file in `airflow/dags/`:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def my_custom_task():
    # Your Python code here
    pass

dag = DAG(
    'my_custom_dag',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily',
)

task = PythonOperator(
    task_id='custom_task',
    python_callable=my_custom_task,
    dag=dag,
)
```

## 📊 Backup Recovery

To restore a database from backup:

```bash
psql -U postgres -d restaurant_db < /tmp/airflow/database_backups/restaurant_db_backup_YYYYMMDD_HHMMSS.sql
```

## 🐛 Troubleshooting

### DAG not appearing
- Check if the file is in `~/airflow/dags/`
- Restart the scheduler
- Check logs for syntax errors: `python -m py_compile airflow/dags/my_dag.py`

### Tasks not running
- Verify scheduler is running: `airflow scheduler`
- Check DAG is not paused in the UI
- Verify cron schedule syntax

### Email not sending
- Test SMTP connection: `python -m smtplib -c <host>:<port>`
- Check SMTP credentials in airflow.cfg
- Verify email configuration in Django settings

### Database backup failures
- Check PostgreSQL is running and accessible
- Verify database credentials
- Ensure sufficient disk space for backups

## 📚 Resources

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [DAG Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [Airflow Concepts](https://airflow.apache.org/docs/apache-airflow/stable/concepts/index.html)
- [Django Integration with Airflow](https://airflow.apache.org/docs/apache-airflow-providers-django/stable/index.html)

## 📞 Support

For issues with:
- **Apache Airflow:** Check the [official documentation](https://airflow.apache.org/)
- **Django integration:** Review your Django settings and environment setup
- **This setup:** Review the DAG files and logs in `~/airflow/logs/`

## ✅ Checklist for Production

Before deploying to production:

- [ ] Set secure passwords for Airflow admin user
- [ ] Configure proper SMTP server for email notifications
- [ ] Set up backup verification and restore procedures
- [ ] Monitor DAG execution and task failures
- [ ] Configure proper logging and alerting
- [ ] Use PostgreSQL backend instead of SQLite
- [ ] Set up proper security and access controls
- [ ] Test all DAGs in a staging environment
- [ ] Document any customizations
- [ ] Set up monitoring and alerts for failed DAGs

---

**Happy Orchestrating! 🎵**
