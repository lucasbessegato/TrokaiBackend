from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    avatar = models.URLField(blank=True)
    fullName = models.TextField(blank=True, null=True)
    reputation_level = models.PositiveSmallIntegerField(default=1)
    reputation_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=100)
    image_url = models.URLField()

    def __str__(self):
        return self.name


class Product(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Available'
        RESERVED = 'reserved', 'Reserved'
        EXCHANGED = 'exchanged', 'Exchanged'

    title = models.CharField(max_length=200)
    description = models.TextField()
    image_url = models.URLField()
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='products', on_delete=models.CASCADE)
    acceptable_exchanges = models.JSONField(default=list)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.AVAILABLE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    url = models.URLField()
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.product.title}: {self.url}"


class UserRating(models.Model):
    from_user = models.ForeignKey(
        User,
        related_name='given_ratings',
        on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        User,
        related_name='received_ratings',
        on_delete=models.CASCADE
    )
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username}: {self.rating}"


class Notification(models.Model):
    class Type(models.TextChoices):
        NEW_PROPOSAL = 'new_proposal', 'New Proposal'
        PROPOSAL_ACCEPTED = 'proposal_accepted', 'Proposal Accepted'
        PROPOSAL_REJECTED = 'proposal_rejected', 'Proposal Rejected'
        EXCHANGE_COMPLETED = 'exchange_completed', 'Exchange Completed'
        NEW_RATING = 'new_rating', 'New Rating'
        LEVEL_UP = 'level_up', 'Level Up'
        SYSTEM = 'system', 'System'
        GENERAL = 'general', 'General'

    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=Type.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link_to = models.CharField(max_length=255, blank=True, null=True)
    related_id = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"


class Proposal(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'
        COMPLETED = 'completed', 'Completed'
        CANCELED = 'canceled', 'Canceled'

    product_offered = models.ForeignKey(
        Product,
        related_name='offers_made',
        on_delete=models.CASCADE
    )
    product_requested = models.ForeignKey(
        Product,
        related_name='offers_received',
        on_delete=models.CASCADE
    )
    from_user = models.ForeignKey(
        User,
        related_name='proposals_sent',
        on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        User,
        related_name='proposals_received',
        on_delete=models.CASCADE
    )
    message = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Proposal {self.id}: {self.from_user.username} → {self.to_user.username}"
