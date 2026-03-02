import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moneycounter.settings')
django.setup()

from django.contrib.auth import authenticate, get_user_model

User = get_user_model()

def test_auth(username, password):
    print(f"Testing auth for user: {username}")
    try:
        user = User.objects.get(username=username)
        print(f"User found: {user.username}, Active: {user.is_active}")
        print(f"Password set: {user.has_usable_password()}")
    except User.DoesNotExist:
        print("User does not exist.")
        return

    auth_user = authenticate(username=username, password=password)
    if auth_user:
        print("Authentication SUCCESS.")
    else:
        print("Authentication FAILED.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3:
        test_auth(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python debug_auth.py <username> <password>")
