#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Consume our database flag before Django parses command options.
    if '--test' in sys.argv:
        os.environ['EHEALTH_TEST_MODE'] = '1'
    elif os.environ.get('RUN_MAIN') != 'true':
        # The reload child inherits this choice after --test has been consumed.
        # A fresh command without --test must still default to PostgreSQL.
        os.environ['EHEALTH_TEST_MODE'] = '0'
    sys.argv = [argument for argument in sys.argv if argument != '--test']
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehealth_hub.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
