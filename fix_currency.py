import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'invent.settings')
django.setup()

from django.contrib.auth.models import User
from auth_app.models import UserProfile

def check_and_fix_currency():
    """Check and fix currency settings for all users"""
    users = User.objects.all()
    
    for user in users:
        print(f"User: {user.username}")
        
        # Check if user has a profile
        if hasattr(user, 'profile'):
            profile = user.profile
            print(f"  Currency: {profile.currency}")
            
            # If currency is not set or invalid, set it to INR
            if not profile.currency or profile.currency not in [choice[0] for choice in UserProfile.CURRENCY_CHOICES]:
                print(f"  Fixing invalid currency: {profile.currency}")
                profile.currency = 'INR'
                profile.save()
                print(f"  Updated to: {profile.currency}")
        else:
            print("  No profile found")
            # Create profile with INR currency
            profile = UserProfile.objects.create(user=user, currency='INR')
            print(f"  Created profile with currency: {profile.currency}")
            
    print("\nAll users processed.")

if __name__ == "__main__":
    check_and_fix_currency()
