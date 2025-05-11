# api/serializers.py
from rest_framework import serializers
from .models import Product, User
import cloudinary.uploader

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


from rest_framework import serializers
import cloudinary.uploader
from .models import User

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
            'bio','location','phone','created_at', 'password',
            'fullName'
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
