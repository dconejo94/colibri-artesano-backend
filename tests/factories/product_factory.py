import uuid
from decimal import Decimal
from app.domain.models.user import User
from app.domain.models.store import Store
from app.domain.models.category import Category
from app.domain.models.product import Product

TEST_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
TEST_STORE_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
TEST_CATEGORY_ID = uuid.UUID("00000000-0000-0000-0000-000000000003")
TEST_PRODUCT_ID = uuid.UUID("00000000-0000-0000-0000-000000000004")


async def seed_products(db):
    user = User(id=TEST_USER_ID, email="test@test.com", password_hash="hash")
    db.add(user)

    store = Store(id=TEST_STORE_ID, owner_id=TEST_USER_ID, name="Test Store")
    db.add(store)

    category = Category(id=TEST_CATEGORY_ID, name="Artesania", slug="artesania")
    db.add(category)

    product = Product(
        id=TEST_PRODUCT_ID,
        store_id=TEST_STORE_ID,
        category_id=TEST_CATEGORY_ID,
        name="Artesania",
        description="Lorem Ipsum",
        base_price=Decimal("10.00"),
    )
    db.add(product)

    await db.commit()
    await db.refresh(product)
    return product
