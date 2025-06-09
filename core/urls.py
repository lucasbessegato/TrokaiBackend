from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from rest_framework import routers, permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_nested import routers as nested_routers

from api.views import CustomAuthToken, ProductImageViewSet, ProductViewSet, ProposalViewSet, UserViewSet

router = routers.DefaultRouter()
router.register(r'users',    UserViewSet)
router.register(r'products', ProductViewSet)
router.register(r'proposal', ProposalViewSet)

# cria um router aninhado para /products/{product_pk}/images
products_router = nested_routers.NestedSimpleRouter(router, r'products', lookup='product')
products_router.register(r'images', ProductImageViewSet, basename='product-images')


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

    # API endpoints
    path('api/', include(router.urls)),
    path('api/', include(products_router.urls)),
    
    path('api-token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),

    # JSON/YAML schema
    re_path(
        r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'
    ),

    # Swagger UI
    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    # ReDoc UI
    path(
        'redoc/',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),

    # redirect raiz para Swagger UI
    path(
        '',
        RedirectView.as_view(pattern_name='schema-swagger-ui', permanent=False)
    ),
]
