from django.urls import path
from . import views

urlpatterns = [
    path('scan/', views.scan_view, name='scan'),  # Endpoint for initiating scan
    path('get_report/', views.get_report_view, name='get_report'),  # Endpoint for generating report
]
