from django.urls import path
from .views import (CategoryDetailView, CategoryListCreateView, ProductDetailView,
                    ProductListCreateView, ProductReviewListCreateView, ProductSearchView,
                    PurchaseProductView, WishlistItemDeleteView, WishlistView)

urlpatterns = [
    path("categories/", CategoryListCreateView.as_view(), name="category-list"),
    path("categories/<int:pk>/", CategoryDetailView.as_view(), name="category-detail"),
    path("products/", ProductListCreateView.as_view(), name="product-list"),
    path("products/search/", ProductSearchView.as_view(), name="product-search"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("products/<int:pk>/purchase/", PurchaseProductView.as_view(), name="product-purchase"),
    path("products/<int:pk>/reviews/", ProductReviewListCreateView.as_view(), name="product-reviews"),
    path("wishlist/", WishlistView.as_view(), name="wishlist"),
    path("wishlist/<int:pk>/", WishlistItemDeleteView.as_view(), name="wishlist-item-delete"),
]