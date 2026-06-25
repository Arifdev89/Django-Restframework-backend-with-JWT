from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'product_name', 'product_description', 'category', 'tags', 'created_at')


class ProductCreateSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(child=serializers.CharField(), required=False, default=list)

    class Meta:
        model = Product
        fields = ('product_name', 'product_description', 'category', 'tags')

    def validate_product_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Product name must be at least 3 characters.")
        return value.strip()

    def validate_category(self, value):
        allowed = ['Smartphones', 'Chargers', 'Back Covers']
        if value not in allowed:
            raise serializers.ValidationError(f"Category must be one of: {', '.join(allowed)}")
        return value


class SearchResultSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    product_name = serializers.CharField()
    product_description = serializers.CharField()
    category = serializers.CharField()
    tags = serializers.ListField(child=serializers.CharField())
    relevance_score = serializers.FloatField()
    rank_reason = serializers.CharField()
