from django.db import models
from apps.visitors.models import Visitor

class Session(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='sessions')
    
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    
    # Traffic Sources
    referrer = models.URLField(max_length=500, null=True, blank=True)
    is_social = models.BooleanField(default=False)
    is_search = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Session {self.session_key} - {self.visitor.visitor_uuid}"
    
    @property
    def duration(self):
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0
