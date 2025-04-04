from django.db import models
from django.utils import timezone

class Image(models.Model):
    file = models.FileField(upload_to="image/", blank=False, null=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ["-created_at", ]
        db_table = 'file'
        
    def __str__(self):
        return self.file.name
