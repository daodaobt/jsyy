from django.urls import path
from . import views

urlpatterns = [
    path('', views.PaymentStatusView.as_view()),
]