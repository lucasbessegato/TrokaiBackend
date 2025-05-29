# api/serializers.py
from rest_framework import serializers
from .models import Product, ProductImage, User
import cloudinary.uploader


class UserSerializer(serializers.ModelSerializer):
    # avatar será só leitura, vem do Cloudinary
    avatar = serializers.URLField(read_only=True)
    # este campo recebe o arquivo de upload
    avatar_file = serializers.ImageField(write_only=True, required=False)
    # senha que vem do frontend (write-only)
    password = serializers.CharField(write_only=True, required=True, min_length=6)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',
            'avatar',    # URL retornada
            'avatar_file',  # arquivo de input
            'reputation_level','reputation_score',
            'phone','created_at', 'password',
            'fullName', 'city', 'state'
        ]

    def _upload_to_cloudinary(self, file):
        result = cloudinary.uploader.upload(
            file,
            folder='avatars/',
            overwrite=True,
        )
        return result['secure_url']

    def create(self, validated_data):
        avatar_file = validated_data.pop('avatar_file', None)
        if avatar_file:
            validated_data['avatar'] = self._upload_to_cloudinary(avatar_file)

        password = validated_data.pop('password')
        # 3) cria o user (sem senha ainda)
        user = super().create(validated_data)
        # 4) faz o hash da senha e salva
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        avatar_file = validated_data.pop('avatar_file', None)
        if avatar_file:
            validated_data['avatar'] = self._upload_to_cloudinary(avatar_file)
        return super().update(instance, validated_data)
    
    
class ProductSerializer(serializers.ModelSerializer):
    # exibe a lista de imagens (read-only)
    images = serializers.SerializerMethodField()
    # aceita a lista de trocas como JSON
    acceptable_exchanges = serializers.JSONField()
    user = UserSerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description',
            'category', 'user', 'acceptable_exchanges',
            'status', 'created_at', 'updated_at', 'user',
            'images',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_images(self, obj):
        # retorna as imagens via ProductImageSerializer
        return ProductImageSerializer(obj.images.all(), many=True).data


class ProductImageSerializer(serializers.ModelSerializer):
    # URL pública da imagem (lida do Cloudinary)
    url = serializers.URLField(read_only=True)
    # campo que recebe o arquivo enviado pelo front
    image_file = serializers.ImageField(write_only=True, required=True)
    # indica se é a imagem principal
    is_main = serializers.BooleanField()

    class Meta:
        model = ProductImage
        fields = ['id', 'url', 'image_file', 'is_main']

    def _upload_to_cloudinary(self, file, product_id):
        """Faz o upload do arquivo para Cloudinary e retorna a URL."""
        result = cloudinary.uploader.upload(
            file,
            folder=f'products/{product_id}/',
            overwrite=True,
        )
        return result['secure_url']

    def create(self, validated_data):
        # pega o arquivo e o is_main
        image_file = validated_data.pop('image_file')
        is_main = validated_data.pop('is_main')
        # recupera o product via contexto (setado na view)
        product = self.context['product']
        # faz upload e preenche a URL
        validated_data['url'] = self._upload_to_cloudinary(image_file, product.id)
        # vincula o product e is_main
        validated_data['product'] = product
        validated_data['is_main'] = is_main
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # se vier novo arquivo, faz upload e atualiza a URL
        image_file = validated_data.pop('image_file', None)
        if image_file:
            instance.url = self._upload_to_cloudinary(image_file, instance.product.id)
        # atualiza is_main se fornecido
        instance.is_main = validated_data.get('is_main', instance.is_main)
        instance.save()
        return instance

