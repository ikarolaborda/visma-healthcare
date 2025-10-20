#!/usr/bin/env python3
"""
Generate secure secrets for Healthcare Patient Management System deployment
"""
import secrets
import string
import sys


def generate_django_secret_key(length=50):
    """Generate a Django SECRET_KEY"""
    chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(chars) for _ in range(length))


def generate_password(length=32):
    """Generate a secure password"""
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--django-secret':
        print(generate_django_secret_key())
    elif len(sys.argv) > 1 and sys.argv[1] == '--password':
        print(generate_password())
    else:
        # Generate all secrets
        print(f"DJANGO_SECRET_KEY={generate_django_secret_key()}")
        print(f"DB_PASSWORD={generate_password()}")
        print(f"RABBITMQ_PASSWORD={generate_password()}")


if __name__ == '__main__':
    main()
