from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
import os
import json

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
        # Password is no longer collected directly at registration

        # Check if user already exists by username or email
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'auth/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'auth/register.html')

        if SUPABASE_AVAILABLE:
            try:
                # Initiate OTP sign-in/signup flow with Supabase
                # This method sends an OTP without requiring a password upfront.
                response = supabase.auth.sign_in_with_otp({
                    "email": email,
                    # Optionally add 'options' if needed, e.g., for redirect URL, but not necessary for basic OTP
                })

                # Store email and username in session to use in OTP verification step
                request.session['registration_email'] = email
                request.session['registration_username'] = username

                messages.info(request, 'Please check your email for the OTP to complete registration.')
                return redirect('verify_otp') # Redirect to the new OTP verification view

            except Exception as supabase_error:
                # Handle potential Supabase errors (e.g., email rate limit, invalid email)
                print(f"Supabase OTP initiation error: {str(supabase_error)}")
                # Check for specific error messages if needed
                error_message = str(supabase_error)
                if "Error sending confirmation otp" in error_message: # Example check
                    messages.error(request, 'Error sending OTP. Please check the email address and try again.')
                else:
                    messages.error(request, f'Could not initiate registration. Error: {error_message}')
                return render(request, 'auth/register.html')
        else:
            messages.error(request, 'Supabase is not available. Cannot register.')
            return render(request, 'auth/register.html')

    return render(request, 'auth/register.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        login_with_otp = request.POST.get('login_with_otp') == 'true'

        if login_with_otp:
            # User wants to login with OTP instead of password
            return initiate_otp_login(request, email)

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


def initiate_otp_login(request, email):
    """Initiate OTP-based login process"""
    if not email:
        messages.error(request, 'Email is required for OTP login')
        return render(request, 'auth/login.html')

    # Check if user exists with this email
    if not User.objects.filter(email=email).exists():
        messages.error(request, 'No user found with this email address')
        return render(request, 'auth/login.html')

    if SUPABASE_AVAILABLE:
        try:
            # Initiate OTP sign-in flow with Supabase
            response = supabase.auth.sign_in_with_otp({
                "email": email,
            })

            # Store email in session for OTP verification
            request.session['login_email'] = email

            messages.info(request, 'Please check your email for the OTP to login.')
            return redirect('verify_login_otp')  # Redirect to OTP verification for login

        except Exception as supabase_error:
            print(f"Supabase OTP login error: {str(supabase_error)}")
            error_message = str(supabase_error)
            if "Error sending confirmation otp" in error_message:
                messages.error(request, 'Error sending OTP. Please check the email address and try again.')
            else:
                messages.error(request, f'Could not initiate OTP login. Error: {error_message}')
            return render(request, 'auth/login.html')
    else:
        messages.error(request, 'Supabase is not available. Cannot use OTP login.')
        return render(request, 'auth/login.html')

def logout_view(request):
    # Sign out from Supabase if available
    if SUPABASE_AVAILABLE:
        supabase.auth.sign_out()

    # Sign out from Django
    logout(request)

    messages.success(request, 'Logged out successfully')
    return redirect('login')


def verify_otp_view(request):
    """Verify OTP for registration"""
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = request.POST.get('otp')
        username = request.session.get('registration_username') # Retrieve username from session

        if not email or not otp or not username:
            messages.error(request, 'Email, OTP, and username are required.')
            # Try to prefill email if available in session
            initial_email = request.session.get('registration_email', '')
            return render(request, 'auth/verify_otp.html', {'email': initial_email})

        if SUPABASE_AVAILABLE:
            try:
                # Verify the OTP with Supabase
                response = supabase.auth.verify_otp({
                    "email": email,
                    "token": otp,
                    "type": "email" # Use 'email' type for OTP verification
                })

                if response.user:
                    # OTP verified successfully, now create the Django user
                    try:
                        # Check again if user exists (edge case)
                        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
                             messages.error(request, 'User already exists. Please try logging in.')
                             return redirect('login')

                        # Create Django user (no password needed initially)
                        user = User.objects.create_user(
                            username=username,
                            email=email
                            # We can set an unusable password or handle password setting later
                        )
                        user.set_unusable_password() # Good practice for passwordless initial signup
                        user.save()

                        # Create SupabaseUser profile to link Django user and Supabase UID
                        SupabaseUser.objects.create(
                            user=user,
                            supabase_uid=response.user.id
                        )

                        # Clean up session variables
                        del request.session['registration_email']
                        del request.session['registration_username']

                        # Log the user in
                        login(request, user, backend='django.contrib.auth.backends.ModelBackend') # Specify backend if needed
                        messages.success(request, 'Registration successful! You are now logged in.')
                        return redirect('dashboard')

                    except Exception as django_error:
                        # Handle potential errors during Django user creation
                        print(f"Django user creation error after OTP verification: {str(django_error)}")
                        messages.error(request, f'Error completing registration: {str(django_error)}')
                        # Consider cleanup if Supabase user was created but Django failed

                else:
                    # This case might indicate an issue with the verify_otp response structure
                    messages.error(request, 'OTP verification failed. Please try again.')

            except Exception as supabase_error:
                # Handle Supabase verification errors (e.g., invalid OTP, expired OTP)
                print(f"Supabase OTP verification error: {str(supabase_error)}")
                messages.error(request, f'Invalid or expired OTP. Please try again. Error: {str(supabase_error)}')
        else:
            messages.error(request, 'Supabase is not available. Cannot verify OTP.')

        # Re-render the form with the email if verification failed
        return render(request, 'auth/verify_otp.html', {'email': email})

    else: # GET request
        # Pre-fill email from session if available
        initial_email = request.session.get('registration_email', '')
        return render(request, 'auth/verify_otp.html', {'email': initial_email})


def verify_login_otp_view(request):
    """Verify OTP for login"""
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = request.POST.get('otp')

        if not email or not otp:
            messages.error(request, 'Email and OTP are required.')
            # Try to prefill email if available in session
            initial_email = request.session.get('login_email', '')
            return render(request, 'auth/verify_otp.html', {'email': initial_email, 'is_login': True})

        if SUPABASE_AVAILABLE:
            try:
                # Verify the OTP with Supabase
                response = supabase.auth.verify_otp({
                    "email": email,
                    "token": otp,
                    "type": "email" # Use 'email' type for OTP verification
                })

                if response.user:
                    # OTP verified successfully, find the Django user
                    try:
                        # Try to find the user by Supabase UID first
                        try:
                            supabase_user = SupabaseUser.objects.get(supabase_uid=response.user.id)
                            user = supabase_user.user
                        except SupabaseUser.DoesNotExist:
                            # If not found, try to find by email
                            user = User.objects.get(email=email)
                            # Create the link between Django user and Supabase
                            SupabaseUser.objects.create(
                                user=user,
                                supabase_uid=response.user.id
                            )

                        # Clean up session variables
                        if 'login_email' in request.session:
                            del request.session['login_email']

                        # Log the user in
                        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                        messages.success(request, 'Login successful!')
                        return redirect('dashboard')

                    except User.DoesNotExist:
                        messages.error(request, 'No user found with this email address.')
                    except Exception as django_error:
                        print(f"Django user retrieval error after OTP verification: {str(django_error)}")
                        messages.error(request, f'Error completing login: {str(django_error)}')

                else:
                    messages.error(request, 'OTP verification failed. Please try again.')

            except Exception as supabase_error:
                print(f"Supabase OTP verification error: {str(supabase_error)}")
                messages.error(request, f'Invalid or expired OTP. Please try again. Error: {str(supabase_error)}')
        else:
            messages.error(request, 'Supabase is not available. Cannot verify OTP.')

        # Re-render the form with the email if verification failed
        return render(request, 'auth/verify_otp.html', {'email': email, 'is_login': True})

    else: # GET request
        # Pre-fill email from session if available
        initial_email = request.session.get('login_email', '')
        return render(request, 'auth/verify_otp.html', {'email': initial_email, 'is_login': True})


def setup_otp_view(request):
    """Show instructions for setting up OTP email template in Supabase"""
    return render(request, 'auth/setup_otp.html')


def resend_otp_view(request):
    """Resend OTP to user's email"""
    if request.method == 'POST':
        try:
            # Parse JSON data from request body
            data = json.loads(request.body)
            email = data.get('email')

            if not email:
                return JsonResponse({'success': False, 'error': 'Email is required'})

            # Check if user exists with this email
            if not User.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'error': 'No user found with this email address'})

            if SUPABASE_AVAILABLE:
                try:
                    # Resend OTP via Supabase
                    response = supabase.auth.sign_in_with_otp({
                        "email": email,
                    })

                    return JsonResponse({'success': True, 'message': 'OTP has been resent to your email'})

                except Exception as supabase_error:
                    error_message = str(supabase_error)
                    print(f"Supabase OTP resend error: {error_message}")
                    return JsonResponse({'success': False, 'error': f'Error sending OTP: {error_message}'})
            else:
                return JsonResponse({'success': False, 'error': 'Supabase is not available. Cannot send OTP.'})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Server error: {str(e)}'})

    # Method not allowed
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
