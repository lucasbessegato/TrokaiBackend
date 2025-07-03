from django.shortcuts import render
from rest_framework.permissions import AllowAny
from rest_framework import viewsets
from .models import Notification, Product, ProductImage, Proposal, User
from .serializers import NotificationSerializer, ProductImageSerializer, ProductSerializer, ProposalSerializer, UserSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q


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
        user = self.request.user
        tab  = self.request.query_params.get('tab')

        if self.action in ('retrieve', 'update', 'partial_update', 'destroy'):
            return Proposal.objects.filter(Q(from_user=user) | Q(to_user=user))

        if tab == 'recebidas':
            return Proposal.objects.filter(to_user=user).order_by('-id')
        if tab == 'enviadas':
            return Proposal.objects.filter(from_user=user).order_by('-id')

        return Proposal.objects.none()

    def perform_create(self, serializer):
        # 1) Salva a proposta
        proposal = serializer.save(from_user=self.request.user)

        # 2) Cria a notificação para quem vai receber a proposta
        Notification.objects.create(
            user=proposal.to_user,
            type=Notification.Type.NEW_PROPOSAL,
            title=f"Nova proposta de {proposal.from_user.username}",
            message=proposal.message,
            related_id=proposal.id,
            link_to=f"/proposals"
        )
        
    def perform_update(self, serializer):
        # 1) pega status antes de atualizar
        proposal = self.get_object()
        old_status = proposal.status

        # 2) salva mudanças
        updated = serializer.save()
        new_status = updated.status

        # 3) se mudou, cria notificação com link_to adequado
        if new_status != old_status:
            # tradutores
            status_map = {
                Proposal.Status.PENDING:   "Pendente",
                Proposal.Status.ACCEPTED:  "Aceita!",
                Proposal.Status.REJECTED:  "Rejeitada",
                Proposal.Status.COMPLETED: "Concluída",
                Proposal.Status.CANCELED:  "Cancelada",
            }
            traduzido = status_map[new_status]

            # define tipo e link_to
            if new_status == Proposal.Status.ACCEPTED:
                notif_type = Notification.Type.PROPOSAL_ACCEPTED
                # quem aceitou é o to_user do objeto
                contato = updated.to_user
                # monta whatsapp: assume número em formato E.164 sem '+'
                whatsapp_url = f"https://wa.me/{contato.phone}"
                link = whatsapp_url
            elif new_status == Proposal.Status.REJECTED:
                notif_type = Notification.Type.PROPOSAL_REJECTED
                link = "/proposals"
            else:
                # para outros status, reutilize GENERAL
                notif_type = Notification.Type.GENERAL
                link = "/proposals"
                
            responsavel  = updated.to_user.fullName or updated.to_user.username

            # nome do produto (aqui o solicitado; ajuste se quiser o oferecido)
            nome_produto = updated.product_requested.title
            action = ''
            if traduzido == 'Aceita!':
                action = 'aceitou'
            elif traduzido == 'Rejeitada':
                action = 'recusou'

            Notification.objects.create(
                user=updated.from_user,         # quem recebe a notificação
                type=notif_type,
                title=f"Sua proposta foi {traduzido}",
                message=f"{responsavel} {action} sua proposta para o produto {nome_produto}",
                related_id=updated.id,
                link_to=link
            )


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
    http_method_names = ['get', 'patch', 'head', 'options']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')