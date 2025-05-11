from django.shortcuts import render

# Create your views here.
# api/views.py
from rest_framework import viewsets
from .models import Product, User
from .serializers import ProductSerializer, UserSerializer
from rest_framework.parsers import MultiPartParser, FormParser

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    parser_classes = (MultiPartParser, FormParser)   # aceita FormData/multipart