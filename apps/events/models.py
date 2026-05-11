from django.db import models
from apps.sessions.models import Session
from apps.pages.models import PageView

class Event(models.Model):
    EVENT_TYPES = (
        ('click', 'Button/Link Click'),
        ('form', 'Form Submission'),
        ('custom', 'Custom Event'),
    )
    
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='events')
    page_view = models.ForeignKey(PageView, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    element_id = models.CharField(max_length=100, null=True, blank=True)
    custom_data = models.JSONField(null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.event_type} - {self.element_id} at {self.timestamp}"
    
    class Meta:
        ordering = ['-timestamp']
