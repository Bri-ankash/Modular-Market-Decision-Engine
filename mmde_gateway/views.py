from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import AnalysisRequest
from mmde_engine import decision_engine


@login_required(login_url='/login/')
def dashboard(request):
    from django.conf import settings
    user = request.user
    history = AnalysisRequest.objects.filter(user=user).order_by('-created_at')[:20]
    return render(request, 'dashboard/app.html', {
        'user': user,
        'history': history,
        'markets': settings.ALL_MARKETS,
        'allowed_markets': user.allowed_markets if user.is_active_subscription else [],
        'modules': [
            'structure','liquidity','trap_detection',
            'price_action','imbalance','volume',
            'momentum','volatility','session',
        ],
    })


@login_required(login_url='/login/')
def analyze(request):
    from django.conf import settings

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({'error': 'Invalid JSON body'}, status=400)
    else:
        data = request.GET.dict()

    market   = data.get('market', 'forex').lower()
    symbol   = data.get('symbol', 'EURUSD').upper()
    interval = data.get('interval', 'H1')
    selected = data.get('selected_modules') or []
    entry    = data.get('entry_price')
    candles  = data.get('candles') or []

    try:
        entry = float(entry) if entry else None
    except Exception:
        entry = None

    # Market access check
    user = request.user
    if not user.is_superuser:
        if not user.is_active_subscription:
            return JsonResponse({
                'error': 'No active subscription. Please upgrade to access markets.',
                'upgrade_url': '/subscription/',
            }, status=403)
        if market not in (user.allowed_markets or []):
            return JsonResponse({
                'error': f'"{market.title()}" is not included in your {user.subscription_plan} plan.',
                'upgrade_url': '/subscription/',
            }, status=403)

    # Need at least 3 candles to do anything meaningful
    if len(candles) < 3:
        return JsonResponse({
            'error': f'Please enter at least 3 candles. You provided {len(candles)}. Use Load Sample or Fetch Live to get started.',
        }, status=400)

    try:
        result = decision_engine.run(
            candles=candles,
            symbol=symbol,
            selected_modules=selected if selected else None,
            entry_price=entry,
            params={'market': market, 'interval': interval},
        )
        result['interval'] = interval
        result['data_points'] = len(candles)

        AnalysisRequest.objects.create(
            user=user,
            market=market,
            symbol=symbol,
            selected_modules=selected,
            result=result,
            duration_ms=result.get('duration_ms', 0),
        )
        return JsonResponse(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'Analysis error: {str(e)}'}, status=500)


@login_required(login_url='/login/')
def market_data_api(request):
    from mmde_engine import market_data
    symbol   = request.GET.get('symbol', 'EURUSD').upper()
    interval = request.GET.get('interval', 'H1')
    limit    = min(int(request.GET.get('count', 50)), 200)
    try:
        result = market_data.fetch(symbol, interval, limit)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e), 'candles': []}, status=400)


@csrf_exempt
def tradingview_webhook(request):
    """
    TradingView Pine Script sends candles here.
    Saves them so user can load + analyse from dashboard.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    candles  = data.get('candles', [])
    symbol   = data.get('symbol', 'UNKNOWN').upper()
    interval = data.get('interval', 'H1')
    market   = data.get('market', 'forex').lower()

    if len(candles) < 3:
        return JsonResponse({'error': 'Need at least 3 candles'}, status=400)

    # Save to DB so dashboard can pick it up
    from .models import TradingViewFeed
    TradingViewFeed.objects.update_or_create(
        user_secret='default',
        defaults={
            'symbol':       symbol,
            'interval':     interval,
            'market':       market,
            'candles_json': json.dumps(candles),
        }
    )

    return JsonResponse({
        'status': 'received',
        'symbol': symbol,
        'interval': interval,
        'candles': len(candles),
        'message': 'Candles saved. Open MMDE dashboard and click Load from TradingView.',
    })


@login_required(login_url='/login/')
def get_tv_feed(request):
    """Dashboard polls this to get latest TradingView candles"""
    from .models import TradingViewFeed
    feed = TradingViewFeed.objects.filter(user_secret='default').first()
    if not feed:
        return JsonResponse({'found': False, 'message': 'No data received from TradingView yet.'})
    return JsonResponse({
        'found':    True,
        'symbol':   feed.symbol,
        'interval': feed.interval,
        'market':   feed.market,
        'candles':  json.loads(feed.candles_json),
        'received': feed.received_at.strftime('%d %b %Y %H:%M:%S UTC'),
    })


@login_required(login_url='/login/')
def subscription(request):
    from django.conf import settings
    from payments.models import Payment

    user = request.user

    if request.method == 'POST':
        plan      = request.POST.get('plan', '').upper()
        mpesa     = request.POST.get('mpesa_code', '').strip().upper()
        plan_data = settings.SUBSCRIPTION_PLANS.get(plan)

        if not plan_data or plan == 'FREE':
            from django.contrib import messages
            messages.error(request, 'Please select a valid paid plan.')
        elif not mpesa or len(mpesa) < 8:
            from django.contrib import messages
            messages.error(request, 'Enter a valid M-Pesa code (e.g. QKJ1234567).')
        else:
            import uuid
            Payment.objects.create(
                user=user,
                plan=plan,
                amount=float(plan_data['price']),
                currency='USD',
                reference=f"MMDE-{uuid.uuid4().hex[:10].upper()}",
                mpesa_code=mpesa,
                status='PENDING',
            )
            from django.contrib import messages
            messages.success(request, f'Payment submitted! Admin will activate your {plan_data["name"]} plan within 24 hours.')
            return redirect('/subscription/')

    pending = Payment.objects.filter(user=user, status='PENDING').last()
    approved = Payment.objects.filter(user=user, status='APPROVED').last()

    return render(request, 'dashboard/subscription.html', {
        'plans':       settings.SUBSCRIPTION_PLANS,
        'user':        user,
        'pending':     pending,
        'approved':    approved,
        'mpesa_till':  '5359428',
    })


def landing(request):
    from django.conf import settings
    modules = [
        ('Structure',      'Higher highs/lows, BOS, CHoCH trend detection'),
        ('Liquidity',      'Stop hunt detection, equal highs & lows'),
        ('Trap Detection', 'Fake breakouts, bull/bear traps, long wicks'),
        ('Price Action',   'Engulfing, hammer, shooting star, 3-candle patterns'),
        ('Imbalance',      'Fair Value Gap (FVG) detection'),
        ('Volume',         'Volume spikes, expansion vs contraction'),
        ('Momentum',       'RSI divergence, ROC acceleration'),
        ('Volatility',     'ATR compression/expansion, breakout readiness'),
        ('Session',        'London, New York, Asian session behaviour'),
    ]
    return render(request, 'landing/index.html', {
        'plans':   settings.SUBSCRIPTION_PLANS,
        'modules': modules,
    })
