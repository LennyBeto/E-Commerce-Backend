from rest_framework import serializers

from .models import Category, Product, Review, WishlistItem


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description", "product_count", "created_at")
        read_only_fields = ("id", "created_at")

    def get_product_count(self, obj):
        return obj.products.count()


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""

    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True, required=False
    )
    in_stock = serializers.ReadOnlyField()
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "price",
            "category",
            "category_id",
            "stock_quantity",
            "in_stock",
            "image_url",
            "created_by",
            "created_date",
        )
        read_only_fields = ("id", "created_date", "created_by")

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value

    def validate_stock_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative.")
        return value


class ProductDetailSerializer(ProductListSerializer):
    """Full serializer for create / retrieve / update."""

    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + (
            "description",
            "updated_at",
            "average_rating",
            "review_count",
        )
        read_only_fields = ProductListSerializer.Meta.read_only_fields + ("updated_at",)

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews.exists():
            return None
        total = sum(r.rating for r in reviews)
        return round(total / reviews.count(), 1)

    def get_review_count(self, obj):
        return obj.reviews.count()

    def create(self, validated_data):
        # Attach the authenticated user as the creator
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["created_by"] = request.user
        return super().create(validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ("id", "product", "user", "rating", "comment", "created_at")
        read_only_fields = ("id", "user", "created_at", "product")

    def validate(self, attrs):
        request = self.context.get("request")
        product = self.context.get("product")
        if product and request:
            if Review.objects.filter(product=product, user=request.user).exists():
                raise serializers.ValidationError("You have already reviewed this product.")
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        product = self.context.get("product")
        return Review.objects.create(
            user=request.user, product=product, **validated_data
        )


class WishlistItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )

    class Meta:
        model = WishlistItem
        fields = ("id", "product", "product_id", "added_at")
        read_only_fields = ("id", "added_at")

    def validate(self, attrs):
        request = self.context.get("request")
        product = attrs.get("product")
        if WishlistItem.objects.filter(user=request.user, product=product).exists():
            raise serializers.ValidationError("This product is already in your wishlist.")
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        return WishlistItem.objects.create(user=request.user, **validated_data)