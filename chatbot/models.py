from django.db import models

class Document(models.Model):
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(blank=True, null=True)  # To store file content

    def __str__(self):
        return self.name
