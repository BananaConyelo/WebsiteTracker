from django.db import models
from apps.sessions.models import Session

class PageView(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='page_views')
    path = models.CharField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)
    scroll_depth_max = models.IntegerField(default=0) # 0 to 100 percentage
    
    def __str__(self):
        return f"{self.path} - {self.timestamp}"
    
    class Meta:
        ordering = ['-timestamp']
