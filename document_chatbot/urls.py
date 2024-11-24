from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from chatbot import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/upload/', views.upload_document),
    path('api/ask/', views.ask_question),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
