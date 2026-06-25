from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination

from .models import Product
from .serializers import ProductSerializer, ProductCreateSerializer, SearchResultSerializer
from .search import search_products
from api.analytics.models import SearchLog


class ProductSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        limit = int(request.query_params.get('limit', 20))
        category_filter = request.query_params.get('category_filter', None)
        page = int(request.query_params.get('page', 1))

        if not query:
            return Response(
                {'error': 'Search query "q" is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if limit < 1 or limit > 100:
            return Response(
                {'error': 'limit must be between 1 and 100.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = Product.objects.all()
        if category_filter:
            queryset = queryset.filter(category__iexact=category_filter)

        ranked_results = search_products(queryset, query)
        total = len(ranked_results)

        # Manual pagination
        start = (page - 1) * limit
        end = start + limit
        paginated = ranked_results[start:end]

        # Log the search
        try:
            SearchLog.objects.create(
                user=request.user,
                query=query,
                results_count=total,
            )
        except Exception:
            pass  # Don't fail search if logging fails

        return Response({
            'query': query,
            'total_results': total,
            'page': page,
            'limit': limit,
            'total_pages': (total + limit - 1) // limit,
            'results': paginated,
        }, status=status.HTTP_200_OK)


class ProductDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)


class ProductByCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, category):
        products = Product.objects.filter(category__iexact=category)
        if not products.exists():
            return Response({'error': f'No products found in category "{category}".'}, status=status.HTTP_404_NOT_FOUND)

        paginator = PageNumberPagination()
        paginator.page_size = int(request.query_params.get('limit', 20))
        page = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ProductCreateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = ProductCreateSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        products = Product.objects.all().order_by('id')
        paginator = PageNumberPagination()
        paginator.page_size = int(request.query_params.get('limit', 20))
        page = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
