import pytest
from decimal import Decimal
from src.domain.entities.product import Product


class TestProductDefaults:
    def test_default_is_active(self):
        product = Product(name="Test")
        assert product.is_active is True

    def test_default_price_zero(self):
        product = Product(name="Test")
        assert product.price_amount == Decimal("0")

    def test_default_currency_usd(self):
        product = Product(name="Test")
        assert product.price_currency == "USD"

    def test_default_stock_zero(self):
        product = Product(name="Test")
        assert product.stock == 0

    def test_default_image_keys_none(self):
        product = Product(name="Test")
        assert product.image_object_key is None
        assert product.thumbnail_object_key is None


class TestProductFields:
    def test_name_set_correctly(self):
        product = Product(name="Laptop")
        assert product.name == "Laptop"

    def test_price_set_correctly(self):
        product = Product(name="Test", price_amount=Decimal("1999.99"))
        assert product.price_amount == Decimal("1999.99")

    def test_stock_set_correctly(self):
        product = Product(name="Test", stock=100)
        assert product.stock == 100

    def test_can_update_is_active(self):
        product = Product(name="Test")
        product.is_active = False
        assert product.is_active is False

    def test_can_set_image_key(self):
        product = Product(name="Test")
        product.image_object_key = "products/123/image.jpg"
        assert product.image_object_key == "products/123/image.jpg"


class TestProductEquality:
    def test_same_instance_equals_itself(self):
        p = Product(name="Test")
        assert p == p

    def test_same_data_and_id_are_equal(self):
        from datetime import datetime, timezone
        from decimal import Decimal
        now = datetime.now(timezone.utc)
        p1 = Product(name="Laptop", price_amount=Decimal("999"), created_at=now, updated_at=now)
        p2 = Product(name="Laptop", price_amount=Decimal("999"), created_at=now, updated_at=now)
        p2.id = p1.id
        assert p1 == p2

    def test_different_names_not_equal(self):
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        p1 = Product(name="A", created_at=now, updated_at=now)
        p2 = Product(name="B", created_at=now, updated_at=now)
        p2.id = p1.id
        assert p1 != p2
