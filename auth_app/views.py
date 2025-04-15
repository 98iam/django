from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
import os

# Try to import Supabase, but handle the case where it's not installed
try:
    from supabase import create_client, Client
    from .models import SupabaseUser

    # Initialize Supabase client
    SUPABASE_URL = "https://ljmzjgzbzvlhxeuwktpu.supabase.co"
    SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxqbXpqZ3pienZsaHhldXdrdHB1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQxOTYwMDUsImV4cCI6MjA1OTc3MjAwNX0.G3UxJDCwtPHDIzD-OpMqptlCwnKI9YsrCfvPJuL0WyI"

    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    SUPABASE_AVAILABLE = True
except ImportError:
    # Supabase is not installed, create dummy objects
    print("Supabase not available. Using Django authentication only.")
    SUPABASE_AVAILABLE = False
    supabase = None

    # Create a dummy SupabaseUser model if it doesn't exist
    try:
        from .models import SupabaseUser
    except ImportError:
        # This is just a placeholder and won't be used
        class SupabaseUser:
            pass

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'auth/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'auth/register.html')

        try:
            # First create the Django user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            # Then try to create the user in Supabase if available
            if SUPABASE_AVAILABLE:
                try:
                    response = supabase.auth.sign_up({
                        "email": email,
                        "password": password,
                    })

                    if response.user:
                        # Create SupabaseUser profile
                        SupabaseUser.objects.create(
                            user=user,
                            supabase_uid=response.user.id
                        )
                except Exception as supabase_error:
                    # If Supabase fails, log the error but continue with Django user
                    print(f"Supabase registration error: {str(supabase_error)}")
                    # We don't want to show this error to the user as the Django user was created successfully

            # Log the user in
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')

        except Exception as e:
            messages.error(request, f'Registration error: {str(e)}')

    return render(request, 'auth/register.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # First try to find the user by email
        try:
            user = User.objects.get(email=email)
            username = user.username

            # Try Django authentication
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('dashboard')
            else:
                # If Django auth fails, try Supabase if available
                if SUPABASE_AVAILABLE:
                    try:
                        # Authenticate with Supabase
                        response = supabase.auth.sign_in_with_password({
                            "email": email,
                            "password": password,
                        })

                        if response.user:
                            # Find the Django user associated with this Supabase user
                            try:
                                supabase_user = SupabaseUser.objects.get(supabase_uid=response.user.id)
                                user = supabase_user.user

                                # Log the user in
                                login(request, user)
                                messages.success(request, 'Login successful!')
                                return redirect('dashboard')
                            except SupabaseUser.DoesNotExist:
                                # Create a SupabaseUser entry for this user
                                django_user = User.objects.get(email=email)
                                SupabaseUser.objects.create(
                                    user=django_user,
                                    supabase_uid=response.user.id
                                )
                                login(request, django_user)
                                messages.success(request, 'Login successful!')
                                return redirect('dashboard')
                        else:
                            messages.error(request, 'Invalid credentials')
                    except Exception as e:
                        messages.error(request, f'Error with Supabase: {str(e)}')
                else:
                    messages.error(request, 'Invalid credentials')
        except User.DoesNotExist:
            # User doesn't exist with this email
            messages.error(request, 'No user found with this email address')
        except User.MultipleObjectsReturned:
            # Multiple users with the same email
            messages.error(request, 'Multiple accounts found with this email. Please contact support.')
        except Exception as e:
            messages.error(request, f'Login error: {str(e)}')

    return render(request, 'auth/login.html')

def logout_view(request):
    # Sign out from Supabase if available
    if SUPABASE_AVAILABLE:
        supabase.auth.sign_out()

    # Sign out from Django
    logout(request)

    messages.success(request, 'Logged out successfully')
    return redirect('login')