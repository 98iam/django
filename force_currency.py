import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'invent.settings')
django.setup()

from django.contrib.auth.models import User
from auth_app.models import UserProfile
from django.db import connection

def force_currency_to_inr():
    """Force all user profiles to use INR currency"""
    # First, make sure all users have profiles
    users = User.objects.all()
    
    for user in users:
        print(f"User: {user.username}")
        
        # Get or create profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        if created:
            print(f"  Created new profile")
        
        # Force currency to INR
        profile.currency = 'INR'
        profile.save()
        print(f"  Set currency to: {profile.currency}")
    
    # Verify with direct SQL query
    with connection.cursor() as cursor:
        cursor.execute("SELECT auth_app_userprofile.currency, auth_user.username FROM auth_app_userprofile JOIN auth_user ON auth_app_userprofile.user_id = auth_user.id")
        rows = cursor.fetchall()
        
        print("\nDatabase check:")
        for row in rows:
            currency, username = row
            print(f"  {username}: {currency}")
    
    print("\nAll users processed.")

if __name__ == "__main__":
    force_currency_to_inr()
