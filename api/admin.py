from django.contrib import admin
from .models import User, Category, Product, ProductImage, Notification
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    list_display = ('id', 'username', 'email', 'avatar', 'reputation_level', 'password', 'fullName', 'city', 'state')
    list_filter  = ('reputation_level',)
    search_fields = ('username', 'email')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'image_url')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'user',
        'category',
        'status',
        'created_at',
        'updated_at',
    )
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    raw_id_fields = ('user', 'category')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'product',
        'is_main',
        'url',
    )
    list_filter = ('is_main', 'product')
    search_fields = ('product__title',)
    raw_id_fields = ('product',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
    )
