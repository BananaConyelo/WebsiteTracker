import uuid
from django.db import models

class Visitor(models.Model):
    visitor_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Device and Technology
    device_type = models.CharField(max_length=50, null=True, blank=True)
    browser_type = models.CharField(max_length=100, null=True, blank=True)
    operating_system = models.CharField(max_length=100, null=True, blank=True)
    
    # Location
    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Visitor {self.visitor_uuid} - {self.ip_address}"
