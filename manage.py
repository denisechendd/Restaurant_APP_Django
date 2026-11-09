#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import subprocess
import sys


def run_devserver(runserver_args):
    """Run the local checks and tests before starting Django's dev server."""
    import django
    from django.core.management import call_command, execute_from_command_line

    django.setup()
    call_command('check')
    call_command('makemigrations', 'bookings', 'website', check=True, dry_run=True)
    call_command('migrate', interactive=False)
    subprocess.run([sys.executable, '-m', 'pytest'], check=True)

    execute_from_command_line([sys.argv[0], 'runserver', *runserver_args])


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_booking.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    if len(sys.argv) > 1 and sys.argv[1] == 'devserver':
        run_devserver(sys.argv[2:])
    else:
        execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
