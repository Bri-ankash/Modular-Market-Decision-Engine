from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json, time
from .models import AnalysisRequest
from mmde_engine import decision_engine

@login_required(login_url='/login/')
def dashboard(request):
    from django.conf import settings
    user = request.user
    history = AnalysisRequest.objects.filter(user=user)[:20]
    plans = settings.SUBSCRIPTION_PLANS
    markets = settings.ALL_MARKETS
    allowed = user.allowed_markets
    return render(request, 'dashboard/app.html', {
        'user': user,
        'history': history,
        'plans': plans,
        'markets': markets,
        'allowed_markets': allowed,
    })

@login_required(login_url='/login/')
def analyze(request):
    """MMDE analysis endpoint — POST or GET"""
    from django.conf import settings

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except:
            data = request.POST.dict()
    else:
        data = request.GET.dict()

    market = data.get('market', 'forex').lower()
    symbol = data.get('symbol', 'EURUSD').upper()
    selected_modules = data.get('selected_modules', [])
    entry_price = float(data.get('entry_price', 0)) or None
    candles = data.get('candles', [])

    # Check access
    if not request.user.can_access_market(market) and not request.user.is_superuser:
        return JsonResponse({
            'error': f'Your plan does not include {market}.',
            'upgrade_url': '/subscription/',
        }, status=403)

    # Run engine
    result = decision_engine.run(
        candles=candles,
        symbol=symbol,
        selected_modules=selected_modules if selected_modules else None,
        entry_price=entry_price,
        params={'market': market},
    )

    # Save to history
    AnalysisRequest.objects.create(
        user=request.user,
        market=market,
        symbol=symbol,
        selected_modules=selected_modules,
        result=result,
        duration_ms=result.get('duration_ms', 0),
    )

    return JsonResponse(result)

def landing(request):
    from django.conf import settings
    return render(request, 'landing/index.html', {
        'plans': settings.SUBSCRIPTION_PLANS,
    })

@login_required(login_url='/login/')
def subscription(request):
    from django.conf import settings
    from payments.models import Payment
    user = request.user
    if request.method == 'POST':
        plan = request.POST.get('plan')
        mpesa_code = request.POST.get('mpesa_code', '').strip().upper()
        if plan in settings.SUBSCRIPTION_PLANS and plan != 'FREE':
            import uuid
            Payment.objects.create(
                user=user,
                plan=plan,
                amount=settings.SUBSCRIPTION_PLANS[plan]['price'],
                currency='USD',
                reference=f"MMDE-{uuid.uuid4().hex[:10].upper()}",
                mpesa_code=mpesa_code,
                status='PENDING',
            )
            from django.contrib import messages
            messages.success(request, 'Payment submitted! Admin will activate your subscription within 24hrs.')
    pending = Payment.objects.filter(user=user, status='PENDING').last()
    return render(request, 'dashboard/subscription.html', {
        'plans': settings.SUBSCRIPTION_PLANS,
        'user': user,
        'pending': pending,
    })
