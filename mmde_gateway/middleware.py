from django.http import JsonResponse

class MarketAccessMiddleware:
    """Block unauthorized market access"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only enforce on analysis endpoints
        if request.path.startswith('/api/mmde/analyze'):
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Authentication required'}, status=401)
            market = request.GET.get('market') or request.POST.get('market', '')
            if market and not request.user.can_access_market(market):
                return JsonResponse({
                    'error': f'Market "{market}" not included in your plan.',
                    'your_plan': request.user.subscription_plan,
                    'upgrade_url': '/subscription/',
                }, status=403)
        return self.get_response(request)
