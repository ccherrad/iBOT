
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', admin.site.urls),
    path('fb-webhook-hundler/',include('Chatbot.urls')),
    path('payment/',include('Post.urls')),
    path('paypal/', include('paypal.standard.ipn.urls')),
]

urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)