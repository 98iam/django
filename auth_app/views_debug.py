from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def debug_user_profile(request):
    """Debug view to check user profile settings"""
    user = request.user
    
    # Check if user has a profile
    has_profile = hasattr(user, 'profile')
    
    response_data = {
        'username': user.username,
        'has_profile': has_profile,
    }
    
    if has_profile:
        profile = user.profile
        response_data.update({
            'currency': profile.currency,
            'language': profile.language,
            'timezone': profile.timezone,
            'date_format': profile.date_format,
        })
    
    return JsonResponse(response_data)
