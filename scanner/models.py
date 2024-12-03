from django.db import models

# Create your models here.
#from django.db import models

#class ScanReport(models.Model):
#    url = models.URLField(max_length=255)
#    tool_name = models.CharField(max_length=100)
#    output = models.TextField()
#    created_at = models.DateTimeField(auto_now_add=True)

#    def __str__(self):
#        return f"Scan Report for {self.url} using {self.tool_name}"
# models.py
from django.db import models

class ScanReport(models.Model):
    url = models.URLField()
    tool_name = models.CharField(max_length=100)
    output = models.TextField()
    scanned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tool_name} - {self.url}"
