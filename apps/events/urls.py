from django.urls import path
from .views import TrackEventView

app_name = 'events'

urlpatterns = [
    path('track/', TrackEventView.as_view(), name='track'),
]
