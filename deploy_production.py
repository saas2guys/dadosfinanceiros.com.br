import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"Running: {description}")
    print(f"Command: {command}")

    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ Success: {description}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {description}")
        print(f"Error output: {e.stderr}")
        return False


def check_environment():
    """Check if all required environment variables are set."""
    required_vars = [
        "SECRET_KEY",
        "DEBUG",
        "DATABASE_URL",
    ]

    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)

    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these environment variables before deploying.")
        return False

    print("✅ All required environment variables are set.")
    return True


def deploy_production():
    """Main deployment function."""
    print("🚀 Starting production deployment for dadosfinanceiros.com.br")
    print("=" * 60)

    if not check_environment():
        sys.exit(1)

    if not run_command(
        "pip install -r requirements.txt", "Installing Python dependencies"
    ):
        sys.exit(1)

    if not run_command(
        "python manage.py collectstatic --noinput", "Collecting static files"
    ):
        sys.exit(1)

    if not run_command("python manage.py migrate", "Running database migrations"):
        sys.exit(1)

    print("\n📝 Creating superuser (if needed)...")
    subprocess.run("python manage.py createsuperuser", shell=True)

    if not run_command("python manage.py check --deploy", "Running deployment checks"):
        print("⚠️  Warning: Deployment checks failed. Please review the issues above.")

    print("\n🎉 Deployment completed successfully!")
    print("\n📋 Post-deployment checklist:")
    print("1. Ensure your web server (nginx/apache) is configured correctly")
    print("2. Set up SSL certificates for HTTPS")
    print("3. Configure your domain DNS to point to your server")
    print("4. Test CSRF token functionality on your production domain")
    print("5. Monitor application logs for any issues")
    print("\n🔐 Security Notes:")
    print("- CSRF protection is enabled and configured for dadosfinanceiros.com.br")
    print("- HTTPS is enforced in production")
    print("- Secure cookies are enabled")
    print("- HSTS is configured")


if __name__ == "__main__":
    deploy_production()
