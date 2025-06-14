from django.shortcuts import render
from rest_framework.permissions import AllowAny
from rest_framework import viewsets
from .models import Product, ProductImage, Proposal, User
from .serializers import ProductImageSerializer, ProductSerializer, ProposalSerializer, UserSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    # para ?search=texto — faz title__icontains=texto
    search_fields = ['title']
    # para ?category=1 — filtra product__category_id=1
    filterset_fields = ['category', 'user']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    def perform_update(self, serializer):
        product = serializer.save(user=self.request.user)
        # Apaga todas as imagens existentes do produto
        product.images.all().delete()
    
    
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
        
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


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
        

class ProposalViewSet(viewsets.ModelViewSet):
    serializer_class = ProposalSerializer
    queryset = Proposal.objects.all()

    def get_queryset(self):
        tab  = self.request.query_params.get('tab')
        user = self.request.user

        if tab == 'recebidas':
            return Proposal.objects.filter(to_user=user)
        if tab == 'enviadas':
            return Proposal.objects.filter(from_user=user)
        return Proposal.objects.none()

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)
