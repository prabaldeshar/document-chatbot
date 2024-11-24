from django.contrib import admin
from .models import Document
# Register your models here.

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'uploaded_at')

admin.site.register(Document, DocumentAdmin)