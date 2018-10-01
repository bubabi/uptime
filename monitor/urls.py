from django.urls import path
from monitor.views import UptimeDashboardView

app_name = 'monitor'

urlpatterns = [
    path('', view=UptimeDashboardView.as_view(), name='dashboard'),
]