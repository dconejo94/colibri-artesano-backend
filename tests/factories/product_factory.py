import uuid
from decimal import Decimal
from app.domain.models.user import User
from app.domain.models.store import Store
from app.domain.models.category import Category
from app.domain.models.product import Product

# Must match _SEED_USER_ID in security.py so get_current_user returns the store owner.
TEST_USER_ID = uuid.UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")
TEST_STORE_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
TEST_CATEGORY_ID = uuid.UUID("00000000-0000-0000-0000-000000000003")
TEST_PRODUCT_ID = uuid.UUID("00000000-0000-0000-0000-000000000004")
TEST_PRODUCT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
TEST_PRODUCT_2_ID = uuid.UUID("00000000-0000-0000-0000-000000000003")

async def seed_products(db):
    user = User(
        id=TEST_USER_ID, email="test@test.com", password_hash="hash", role="vendor"
    )
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

    product2 = Product(
        id=TEST_PRODUCT_2_ID,
        store_id=TEST_STORE_ID,
        category_id=TEST_CATEGORY_ID,
        name="Tela",
        description="Lorem Ipsum",
        base_price=Decimal("7.00"),
    )

    db.add(product)

    await db.commit()
    await db.refresh(product)
    return product
