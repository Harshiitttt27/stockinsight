from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from .models import Prediction
from .ml import predict_stock_and_generate_plots  # moved logic to ml.py for cleaner structure
import os

class PredictView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ticker = request.data.get("ticker", "").upper().strip()
        if not ticker:
            return Response({"error": "Ticker is required"}, status=400)

        try:
            price, mse, rmse, r2, plot1_path, plot2_path = predict_stock_and_generate_plots(ticker)

            # Convert absolute to relative paths for ImageField
            plot1_rel = os.path.relpath(plot1_path, settings.MEDIA_ROOT)
            plot2_rel = os.path.relpath(plot2_path, settings.MEDIA_ROOT)

            prediction = Prediction.objects.create(
                user=request.user,
                ticker=ticker,
                next_day_price=price,
                mse=mse,
                rmse=rmse,
                r2=r2,
                plot_1=plot1_rel,
                plot_2=plot2_rel
            )

            return Response({
                "next_day_price": price,
                "mse": mse,
                "rmse": rmse,
                "r2": r2,
                "plot_urls": [
                    request.build_absolute_uri(settings.MEDIA_URL + prediction.plot_1.name),
                    request.build_absolute_uri(settings.MEDIA_URL + prediction.plot_2.name)
                ]
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)


class PredictionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ticker = request.query_params.get("ticker", "").upper()
        queryset = Prediction.objects.filter(user=request.user)
        if ticker:
            queryset = queryset.filter(ticker=ticker)

        results = []
        for p in queryset.order_by('-created_at'):
            results.append({
                "ticker": p.ticker,
                "next_day_price": p.next_day_price,
                "created_at": p.created_at,
                "plot_urls": [
                    request.build_absolute_uri(settings.MEDIA_URL + p.plot_1.name),
                    request.build_absolute_uri(settings.MEDIA_URL + p.plot_2.name)
                ]
            })
        return Response(results)

from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["GET"])
def health_check(request):
    return Response({"status": "ok"})
