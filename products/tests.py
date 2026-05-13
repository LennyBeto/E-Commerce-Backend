from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from .models import Category, Product, Review


def make_user(username="user", password="TestPass123!"):
    return User.objects.create_user(
        username=username, email=f"{username}@test.com", password=password)

def make_category(name="Electronics"):
    return Category.objects.create(name=name, slug=name.lower())

def make_product(category, user, name="Widget", price="49.99", stock=10):
    return Product.objects.create(name=name, price=Decimal(price),
                                  category=category, stock_quantity=stock, created_by=user)


class CategoryTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.client.force_authenticate(user=self.user)

    def test_create_category(self):
        r = self.client.post(reverse("category-list"), {"name": "Books", "slug": "books"})
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_list_categories_public(self):
        self.client.logout()
        r = self.client.get(reverse("category-list"))
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_unauthenticated_create_denied(self):
        self.client.logout()
        r = self.client.post(reverse("category-list"), {"name": "Toys", "slug": "toys"})
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)


class ProductCRUDTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.other = make_user("other")
        self.cat = make_category()
        self.product = make_product(self.cat, self.user)

    def test_create_product(self):
        self.client.force_authenticate(user=self.user)
        r = self.client.post(reverse("product-list"), {
            "name": "Laptop", "price": "999.99",
            "category_id": self.cat.pk, "stock_quantity": 5})
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_list_products_public(self):
        r = self.client.get(reverse("product-list"))
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_get_product_detail(self):
        r = self.client.get(reverse("product-detail", kwargs={"pk": self.product.pk}))
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_404_for_missing_product(self):
        r = self.client.get(reverse("product-detail", kwargs={"pk": 99999}))
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_can_update(self):
        self.client.force_authenticate(user=self.user)
        r = self.client.patch(reverse("product-detail", kwargs={"pk": self.product.pk}),
                              {"price": "39.99"})
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_non_owner_cannot_update(self):
        self.client.force_authenticate(user=self.other)
        r = self.client.patch(reverse("product-detail", kwargs={"pk": self.product.pk}),
                              {"price": "1.00"})
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete(self):
        self.client.force_authenticate(user=self.user)
        r = self.client.delete(reverse("product-detail", kwargs={"pk": self.product.pk}))
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)


class SearchFilterTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        elec = make_category("Electronics")
        books = make_category("Books")
        make_product(elec, self.user, "Laptop Pro", "1200.00", stock=5)
        make_product(elec, self.user, "Mouse", "25.00", stock=0)
        make_product(books, self.user, "Django Book", "35.00", stock=20)

    def test_search_by_name(self):
        r = self.client.get(reverse("product-search") + "?q=laptop")
        self.assertEqual(r.data["count"], 1)

    def test_search_by_category(self):
        r = self.client.get(reverse("product-search") + "?q=Electronics")
        self.assertEqual(r.data["count"], 2)

    def test_filter_price_range(self):
        r = self.client.get(reverse("product-list") + "?min_price=30&max_price=100")
        self.assertEqual(r.data["count"], 1)

    def test_filter_in_stock(self):
        r = self.client.get(reverse("product-list") + "?in_stock=true")
        self.assertEqual(r.data["count"], 2)

    def test_filter_by_category(self):
        r = self.client.get(reverse("product-list") + "?category=Books")
        self.assertEqual(r.data["count"], 1)


class ReviewTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.product = make_product(make_category(), self.user)
        self.url = reverse("product-reviews", kwargs={"pk": self.product.pk})

    def test_submit_review(self):
        self.client.force_authenticate(user=self.user)
        r = self.client.post(self.url, {"rating": 4, "comment": "Great!"})
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_cannot_review_twice(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(self.url, {"rating": 4})
        r = self.client.post(self.url, {"rating": 5})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)


class StockTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.product = make_product(make_category(), self.user, stock=10)
        self.client.force_authenticate(user=self.user)

    def test_purchase_reduces_stock(self):
        self.client.post(reverse("product-purchase", kwargs={"pk": self.product.pk}),
                         {"quantity": 3})
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 7)

    def test_purchase_exceeds_stock(self):
        r = self.client.post(reverse("product-purchase", kwargs={"pk": self.product.pk}),
                             {"quantity": 99})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)