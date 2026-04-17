from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import MMDEUser
import urllib.parse, urllib.request, json, secrets
from django.conf import settings


def login_view(request):
    if request.user.is_authenticated:
        return redirect('/app/')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '').strip()

        user = None

        # Try username=email directly
        user = authenticate(request, username=email, password=password)

        # If that fails, find by email then authenticate
        if not user:
            try:
                u = MMDEUser.objects.get(email__iexact=email)
                user = authenticate(request, username=u.username, password=password)
            except MMDEUser.DoesNotExist:
                pass

        # Last resort — check password directly
        if not user:
            try:
                u = MMDEUser.objects.get(email__iexact=email)
                if u.check_password(password) and u.is_active:
                    user = u
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
            except MMDEUser.DoesNotExist:
                pass

        if user:
            login(request, user)
            return redirect('/app/')
        else:
            messages.error(request, 'Email or password is incorrect. Please try again.')

    return render(request, 'auth/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('/app/')
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '').strip()
        name = request.POST.get('name', '').strip()
        if MMDEUser.objects.filter(email__iexact=email).exists():
            messages.error(request, 'This email is already registered. Please login.')
        elif len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
        else:
            u = MMDEUser.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name.split()[0] if name else '',
                last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else '',
            )
            login(request, u, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('/app/')
    return render(request, 'auth/register.html')


def logout_view(request):
    logout(request)
    return redirect('/')


def google_login(request):
    client_id = settings.GOOGLE_CLIENT_ID
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    if not client_id:
        messages.error(request, 'Google login not configured yet.')
        return redirect('/login/')
    state = secrets.token_urlsafe(16)
    request.session['oauth_state'] = state
    params = urllib.parse.urlencode({
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state,
    })
    return redirect(f'https://accounts.google.com/o/oauth2/v2/auth?{params}')


def google_callback(request):
    code = request.GET.get('code')
    error = request.GET.get('error')
    if error or not code:
        messages.error(request, 'Google sign-in was cancelled.')
        return redirect('/login/')
    try:
        token_data = urllib.parse.urlencode({
            'code': code,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': settings.GOOGLE_REDIRECT_URI,
            'grant_type': 'authorization_code',
        }).encode()
        req = urllib.request.Request('https://oauth2.googleapis.com/token', data=token_data)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        resp = urllib.request.urlopen(req, timeout=10)
        token_json = json.loads(resp.read())
        access_token = token_json.get('access_token')
        req2 = urllib.request.Request('https://www.googleapis.com/oauth2/v2/userinfo')
        req2.add_header('Authorization', f'Bearer {access_token}')
        resp2 = urllib.request.urlopen(req2, timeout=10)
        user_info = json.loads(resp2.read())
        email = user_info.get('email', '').lower()
        name = user_info.get('name', email.split('@')[0])
        if not email:
            messages.error(request, 'Could not get email from Google.')
            return redirect('/login/')
        user = MMDEUser.objects.filter(email__iexact=email).first()
        if not user:
            user = MMDEUser.objects.create_user(
                username=email, email=email,
                password=secrets.token_hex(16),
                first_name=name.split()[0] if name else '',
            )
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, f'Welcome, {user.first_name or name}!')
        return redirect('/app/')
    except Exception as e:
        print(f'[OAuth] {e}')
        messages.error(request, 'Google sign-in failed. Please use email/password.')
        return redirect('/login/')
