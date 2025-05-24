from django.shortcuts import render
from rest_framework.permissions import AllowAny
from rest_framework import viewsets
from .models import Product, ProductImage, User
from .serializers import ProductImageSerializer, ProductSerializer, UserSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def perform_create(self, serializer):
        # define o dono do produto como o usuário autenticado
        serializer.save(user=self.request.user)
    
    
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)
    
    
class ProductImageViewSet(viewsets.ModelViewSet):
    """
    Endpoint para /products/{product_pk}/images/
    GET, POST, PUT, DELETE das imagens de um produto.
    """
    serializer_class = ProductImageSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        # passa o product para o serializer
        context = super().get_serializer_context()
        context['product'] = Product.objects.get(pk=self.kwargs['product_pk'])
        return context

    def perform_create(self, serializer):
        # create() do serializer já recebe o product via context
        serializer.save()


class CustomAuthToken(ObtainAuthToken):
    """Gera o token e retorna também os dados do usuário."""
    def post(self, request, *args, **kwargs):
        # valida username+password
        serializer = self.serializer_class(
            data=request.data, 
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        # pega o usuário autenticado
        user = serializer.validated_data['user']
        # busca ou cria o token dele
        token, _ = Token.objects.get_or_create(user=user)

        # serializa o usuário (vai incluir id, username, email, avatar, etc)
        user_data = UserSerializer(user, context={'request': request}).data

        # retorna token + dados do user
        return Response({
            'token': token.key,
            'user':  user_data
        })