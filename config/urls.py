"""
URL configuration for config project.

Rutas principales de la API:
- /admin/               -> panel de administración de Django
- /api/health/          -> chequeo de salud (público)
- /api/token/           -> obtener par de tokens JWT (access + refresh)
- /api/token/refresh/   -> renovar el access token
- /api/                 -> rutas generadas por el router de DRF (ViewSets)
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from config.views import health

# Router de DRF (todavía sin rutas registradas).
router = DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health, name='health'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('core.urls')),
    path('api/', include(router.urls)),
]
