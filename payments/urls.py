from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
]
