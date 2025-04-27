from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from api.views import ProductViewSet
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

router = routers.DefaultRouter()
router.register(r'products', ProductViewSet)
# ... registre aqui os outros ViewSets (Category, User, etc.) ...

schema_view = get_schema_view(
   openapi.Info(
      title="Trokaí API",
      default_version='v1',
      description="Documentação Swagger da API do Trokaí",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    # Swagger UI
    path('swagger(<format>\.json|\.yaml)', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/',          schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/',            schema_view.with_ui('redoc',   cache_timeout=0), name='schema-redoc'),
]
