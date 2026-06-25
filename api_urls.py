from django.urls import path
from .views import (
    ProductSearchView,
    ProductDetailView,
    ProductByCategoryView,
    ProductCreateView,
    ProductListView,
)

urlpatterns = [
    path('search', ProductSearchView.as_view(), name='product-search'),
    path('list', ProductListView.as_view(), name='product-list'),
    path('create', ProductCreateView.as_view(), name='product-create'),
    path('<int:pk>', ProductDetailView.as_view(), name='product-detail'),
    path('category/<str:category>', ProductByCategoryView.as_view(), name='product-by-category'),
]
