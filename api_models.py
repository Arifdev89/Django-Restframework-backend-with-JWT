from django.db import models


class Product(models.Model):
    product_name = models.CharField(max_length=255, db_index=True)
    product_description = models.TextField()
    category = models.CharField(max_length=100, db_index=True)
    tags = models.JSONField(default=list)  # stored as list of strings
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'products'
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['product_name']),
        ]

    def __str__(self):
        return self.product_name
