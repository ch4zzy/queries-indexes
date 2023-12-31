from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import HashIndex, BTreeIndex, GistIndex, GinIndex
from django.db import models
from django.db.models import CharField


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class Order(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    paid = models.BooleanField(default=False)
    order_json = models.JSONField()
    status = ArrayField(
        models.JSONField(default=dict, blank=True, null=True),
        blank=True,
        null=True,
    )
    email_gin_index = GinIndex(fields=['email'], name='email_gin_idx', opclasses=['gin_trgm_ops'])

    class Meta:
        indexes = [
            BTreeIndex(
                fields=["email"],
                name="email_paid_idx_btree",
                condition=models.Q(paid=True)
            ),
            GinIndex(
                fields=["status"],
                name="status_idx_gin"
            ),
            GinIndex(
                fields=["email"],
                name="email_idx_gin",
                opclasses=["gin_trgm_ops"],
                condition=models.Q(paid=True),
            ),
        ]


    def __str__(self) -> str:
        return f"Order {self.id}"
