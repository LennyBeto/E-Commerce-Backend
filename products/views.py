from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from core.pagination import StandardResultsPagination
from core.permissions import IsOwnerOrReadOnly

from .filters import ProductFilter
from .models import Category, Product, Review, WishlistItem
from .serializers import (
    CategorySerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    ReviewSerializer,
    WishlistItemSerializer,
)


# ─── Category Views ──────────────────────────────────────────────────────────

class CategoryListCreateView(generics.ListCreateAPIView):
    """
    GET  /categories/        — List all categories
    POST /categories/        — Create a category (authenticated)
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]
    pagination_class = None  # Return all categories without pagination


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /categories/{id}/  — Retrieve category
    PUT    /categories/{id}/  — Update category (authenticated)
    DELETE /categories/{id}/  — Delete category (authenticated)
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# ─── Product Views ───────────────────────────────────────────────────────────

class ProductListCreateView(generics.ListCreateAPIView):
    """
    GET  /products/          — List products with filtering & pagination
    POST /products/          — Create product (authenticated)

    Query params:
      search       — partial match on name or category name
      category     — exact category name (case-insensitive)
      min_price    — minimum price
      max_price    — maximum price
      in_stock     — true/false
      ordering     — price, -price, created_date, -created_date, name
      page         — page number
      page_size    — items per page (max 100)
    """

    queryset = Product.objects.select_related("category", "created_by").all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "description", "category__name"]
    ordering_fields = ["price", "created_date", "name", "stock_quantity"]
    ordering = ["-created_date"]
    pagination_class = StandardResultsPagination

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProductDetailSerializer
        return ProductListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /products/{id}/   — Retrieve product
    PUT    /products/{id}/   — Full update (owner only)
    PATCH  /products/{id}/   — Partial update (owner only)
    DELETE /products/{id}/   — Delete (owner only)
    """

    queryset = Product.objects.select_related("category", "created_by").all()
    serializer_class = ProductDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        product.delete()
        return Response(
            {"message": f'Product "{product.name}" deleted successfully.'},
            status=status.HTTP_204_NO_CONTENT,
        )


class ProductSearchView(generics.ListAPIView):
    """
    GET /products/search/?q=laptop
    Dedicated search endpoint with partial name and category matching.
    Supports all the same filter/ordering params as the list view.
    """

    serializer_class = ProductListSerializer
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ProductFilter
    ordering_fields = ["price", "created_date", "name"]

    def get_queryset(self):
        q = self.request.query_params.get("q", "").strip()
        if not q:
            return Product.objects.none()

        return (
            Product.objects.select_related("category", "created_by")
            .filter(
                Q(name__icontains=q) | Q(category__name__icontains=q) | Q(description__icontains=q)
            )
            .distinct()
        )

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        q = request.query_params.get("q", "")
        response.data["query"] = q
        return response


# ─── Review Views ─────────────────────────────────────────────────────────────

class ProductReviewListCreateView(generics.ListCreateAPIView):
    """
    GET  /products/{id}/reviews/   — List reviews for a product
    POST /products/{id}/reviews/   — Submit a review (authenticated, once per user)
    """

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsPagination

    def get_product(self):
        return generics.get_object_or_404(Product, pk=self.kwargs["pk"])

    def get_queryset(self):
        return Review.objects.filter(product=self.get_product()).select_related("user")

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["product"] = self.get_product()
        return ctx

    def perform_create(self, serializer):
        serializer.save()


# ─── Wishlist Views ───────────────────────────────────────────────────────────

class WishlistView(generics.ListCreateAPIView):
    """
    GET  /wishlist/   — View your wishlist (authenticated)
    POST /wishlist/   — Add a product to wishlist (authenticated)
    """

    serializer_class = WishlistItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination

    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user).select_related("product")


class WishlistItemDeleteView(generics.DestroyAPIView):
    """
    DELETE /wishlist/{id}/  — Remove item from wishlist (authenticated)
    """

    serializer_class = WishlistItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        item = self.get_object()
        item.delete()
        return Response({"message": "Removed from wishlist."}, status=status.HTTP_204_NO_CONTENT)


# ─── Stock Management ─────────────────────────────────────────────────────────

class PurchaseProductView(APIView):
    """
    POST /products/{id}/purchase/
    Reduces stock by the requested quantity.
    Body: {"quantity": 2}
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        product = generics.get_object_or_404(Product, pk=pk)
        quantity = int(request.data.get("quantity", 1))

        if quantity < 1:
            return Response(
                {"error": "Quantity must be at least 1."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            product.reduce_stock(quantity)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "message": f"Purchased {quantity}× {product.name}.",
                "remaining_stock": product.stock_quantity,
            }
        )