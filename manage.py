#!/usr/bin/env python
import os, sys, configurations

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyconde.settings")
    os.environ.setdefault('DJANGO_CONFIGURATION', 'Base')

    from configurations.management import execute_from_command_line

    execute_from_command_line(sys.argv)