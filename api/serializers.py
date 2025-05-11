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
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',
            'avatar',    # URL retornada
            'avatar_file',  # arquivo de input
            'reputation_level','reputation_score',
            'bio','location','phone','created_at'
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
        return super().create(validated_data)

    def update(self, instance, validated_data):
        avatar_file = validated_data.pop('avatar_file', None)
        if avatar_file:
            validated_data['avatar'] = self._upload_to_cloudinary(avatar_file)
        return super().update(instance, validated_data)
