from django.contrib import admin
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # API
    path('api/product/', include('product.urls')),
    path('api/currency/', include('currency.urls')),
    path('api/stock/', include('store.urls')),
    path('api/user/', include('user.urls')),
    path('api/files/', include('files.urls')),
    path('api/reception/', include('reception.urls')),
    path('api/order/', include('order.urls')),
    path('api/client/', include('client.urls')),
    path('api/settings/', include('settings.urls')),
    path('api/installment/', include('installment.urls')),
    
    # ADMIN
    path('admin/', admin.site.urls),

    # JWT
    path('api/auth/', include('auth.urls')),

    # Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui')


]
if settings.DEBUG:
    urlpatterns.append(
        path('__debug__/', include('debug_toolbar.urls')),

    )
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)