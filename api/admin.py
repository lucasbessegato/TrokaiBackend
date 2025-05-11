from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import User, Category

@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    # exibe colunas na listagem
    list_display = ('id', 'username', 'email', 'avatar', 'reputation_level', 'password', 'fullName')
    list_filter  = ('reputation_level',)
    search_fields = ('username', 'email')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'image_url')
    search_fields = ('name',)
