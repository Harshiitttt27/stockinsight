from django.urls import path
from .views import PredictView, PredictionListView

urlpatterns = [
    path('predict/', PredictView.as_view(), name='predict'),
    path('predictions/', PredictionListView.as_view(), name='predictions'),
]
