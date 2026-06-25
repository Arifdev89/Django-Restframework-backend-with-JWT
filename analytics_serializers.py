from rest_framework import serializers
from .models import SearchLog


class SearchLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = SearchLog
        fields = ('id', 'username', 'query', 'results_count', 'searched_at')
