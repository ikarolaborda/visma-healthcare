#!/usr/bin/env python3
"""
Secret Generator for Healthcare Application
Generates secure random secrets for deployment
"""

import secrets
import string
import sys
import os


def generate_django_secret_key(length=50):
    """Generate a secure Django SECRET_KEY"""
    chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(chars) for _ in range(length))


def generate_password(length=32):
    """Generate a secure password"""
    chars = string.ascii_letters + string.digits + '!@#$%^&*-_=+'
    return ''.join(secrets.choice(chars) for _ in range(length))


def generate_secrets_file(output_file):
    """Generate secrets YAML file"""

    django_key = generate_django_secret_key()
    db_password = generate_password()
    rabbitmq_password = generate_password()

    secrets_content = f"""---
# Auto-generated secrets - DO NOT COMMIT TO VERSION CONTROL
# Generated: {os.popen('date').read().strip()}

django_secret_key: "{django_key}"
db_password: "{db_password}"
rabbitmq_password: "{rabbitmq_password}"
"""

    # Ensure directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Write secrets file
    with open(output_file, 'w') as f:
        f.write(secrets_content)

    # Set secure permissions
    os.chmod(output_file, 0o600)

    print(f"✓ Secrets generated and saved to {output_file}")
    print(f"✓ File permissions set to 600 (owner read/write only)")

    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate-secrets.py <output_file>")
        sys.exit(1)

    output_file = sys.argv[1]

    try:
        generate_secrets_file(output_file)
        sys.exit(0)
    except Exception as e:
        print(f"✗ Error generating secrets: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
