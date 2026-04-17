from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import MMDEUser

def login_view(request):
    if request.user.is_authenticated: return redirect('/app/')
    if request.method == 'POST':
        email = request.POST.get('email','').strip()
        password = request.POST.get('password','').strip()
        user = authenticate(request, username=email, password=password)
        if not user:
            # try with email
            try:
                u = MMDEUser.objects.get(email=email)
                user = authenticate(request, username=u.username, password=password)
            except: pass
        if user:
            login(request, user)
            return redirect('/app/')
        messages.error(request, 'Invalid email or password.')
    return render(request, 'auth/login.html')

def register_view(request):
    if request.user.is_authenticated: return redirect('/app/')
    if request.method == 'POST':
        email = request.POST.get('email','').strip()
        password = request.POST.get('password','').strip()
        name = request.POST.get('name','').strip()
        if MMDEUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        elif len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
        else:
            import uuid
            user = MMDEUser.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name,
            )
            login(request, user)
            return redirect('/app/')
    return render(request, 'auth/register.html')

def logout_view(request):
    logout(request)
    return redirect('/')


import urllib.parse, urllib.request, json, secrets
from django.conf import settings

def google_login(request):
    """Redirect to Google OAuth"""
    client_id = settings.GOOGLE_CLIENT_ID
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    state = secrets.token_urlsafe(16)
    request.session['oauth_state'] = state
    params = urllib.parse.urlencode({
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state,
        'access_type': 'offline',
    })
    return redirect(f'https://accounts.google.com/o/oauth2/v2/auth?{params}')


def google_callback(request):
    """Handle Google OAuth callback"""
    from django.contrib import messages
    from django.contrib.auth import login
    code = request.GET.get('code')
    error = request.GET.get('error')

    if error or not code:
        messages.error(request, 'Google sign-in was cancelled.')
        return redirect('/login/')

    # Exchange code for token
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

        # Get user info
        req2 = urllib.request.Request(f'https://www.googleapis.com/oauth2/v2/userinfo')
        req2.add_header('Authorization', f'Bearer {access_token}')
        resp2 = urllib.request.urlopen(req2, timeout=10)
        user_info = json.loads(resp2.read())

        email = user_info.get('email')
        name = user_info.get('name', email.split('@')[0] if email else 'User')
        google_id = user_info.get('id', '')

        if not email:
            messages.error(request, 'Could not get email from Google.')
            return redirect('/login/')

        # Find or create user
        user = MMDEUser.objects.filter(email=email).first()
        if not user:
            user = MMDEUser.objects.create_user(
                username=email,
                email=email,
                password=secrets.token_hex(16),
                first_name=name.split()[0] if name else '',
                last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else '',
            )
            user.google_id = google_id
            user.save()
            messages.success(request, f'Welcome, {name}! Your account has been created.')
        else:
            messages.success(request, f'Welcome back, {user.first_name or name}!')

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('/app/')

    except Exception as e:
        messages.error(request, f'Google sign-in failed. Please try again.')
        print(f'[OAuth Error] {e}')
        return redirect('/login/')


import urllib.parse, urllib.request, json, secrets
from django.conf import settings

def google_login(request):
    """Redirect to Google OAuth"""
    client_id = settings.GOOGLE_CLIENT_ID
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    state = secrets.token_urlsafe(16)
    request.session['oauth_state'] = state
    params = urllib.parse.urlencode({
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state,
        'access_type': 'offline',
    })
    return redirect(f'https://accounts.google.com/o/oauth2/v2/auth?{params}')


def google_callback(request):
    """Handle Google OAuth callback"""
    from django.contrib import messages
    from django.contrib.auth import login
    code = request.GET.get('code')
    error = request.GET.get('error')

    if error or not code:
        messages.error(request, 'Google sign-in was cancelled.')
        return redirect('/login/')

    # Exchange code for token
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

        # Get user info
        req2 = urllib.request.Request(f'https://www.googleapis.com/oauth2/v2/userinfo')
        req2.add_header('Authorization', f'Bearer {access_token}')
        resp2 = urllib.request.urlopen(req2, timeout=10)
        user_info = json.loads(resp2.read())

        email = user_info.get('email')
        name = user_info.get('name', email.split('@')[0] if email else 'User')
        google_id = user_info.get('id', '')

        if not email:
            messages.error(request, 'Could not get email from Google.')
            return redirect('/login/')

        # Find or create user
        user = MMDEUser.objects.filter(email=email).first()
        if not user:
            user = MMDEUser.objects.create_user(
                username=email,
                email=email,
                password=secrets.token_hex(16),
                first_name=name.split()[0] if name else '',
                last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else '',
            )
            user.google_id = google_id
            user.save()
            messages.success(request, f'Welcome, {name}! Your account has been created.')
        else:
            messages.success(request, f'Welcome back, {user.first_name or name}!')

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('/app/')

    except Exception as e:
        messages.error(request, f'Google sign-in failed. Please try again.')
        print(f'[OAuth Error] {e}')
        return redirect('/login/')
