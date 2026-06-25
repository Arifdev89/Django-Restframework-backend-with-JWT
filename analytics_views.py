from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count

from .models import SearchLog
from .serializers import SearchLogSerializer


class MySearchHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = SearchLog.objects.filter(user=request.user)[:50]
        serializer = SearchLogSerializer(logs, many=True)
        return Response({
            'count': logs.count(),
            'history': serializer.data,
        })


class TopSearchesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        top = (
            SearchLog.objects
            .values('query')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        return Response({'top_searches': list(top)})
