from .models import UserProfile

def user_profile(request):
    """
    Context processor to add user profile to all templates
    """
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            return {'user_profile': profile}
        except UserProfile.DoesNotExist:
            return {'user_profile': None}
    return {'user_profile': None}
