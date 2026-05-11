from django.urls import path
from .views import DashboardHomeView, AudienceView, BehaviorView, EventsView, TimeBasedView

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardHomeView.as_view(), name='home'),
    path('audience/', AudienceView.as_view(), name='audience'),
    path('behavior/', BehaviorView.as_view(), name='behavior'),
    path('time/', TimeBasedView.as_view(), name='time'),
    path('events/', EventsView.as_view(), name='events'),
]
