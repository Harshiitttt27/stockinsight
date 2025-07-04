# stock_insight/middleware.py

from django.utils.timezone import now
from django.http import JsonResponse
from api.models import Prediction


class QuotaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.path.startswith('/api/v1/predict/'):
            if hasattr(request.user, 'userprofile') and not request.user.userprofile.is_pro:
                today = now().date()
                count = Prediction.objects.filter(user=request.user, created__date=today).count()
                if count >= 5:
                    return JsonResponse({
                        "detail": "Free tier prediction limit reached. Upgrade to Pro."
                    }, status=429)
        return self.get_response(request)
