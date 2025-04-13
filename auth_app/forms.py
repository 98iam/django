from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'profile_image', 'language', 'timezone', 'date_format', 'currency']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(UserProfileForm, self).__init__(*args, **kwargs)

        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

    def save(self, user=None, commit=True):
        profile = super(UserProfileForm, self).save(commit=False)

        if user:
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()

            profile.user = user

        if commit:
            profile.save()

        return profile

class NotificationSettingsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['email_notifications', 'low_stock_alerts', 'order_updates']

    def __init__(self, *args, **kwargs):
        super(NotificationSettingsForm, self).__init__(*args, **kwargs)
        self.fields['email_notifications'].label = "Enable email notifications"
        self.fields['low_stock_alerts'].label = "Receive alerts when products are low in stock"
        self.fields['order_updates'].label = "Receive updates about orders"

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(CustomPasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})
