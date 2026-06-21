import uuid
from decimal import Decimal
from app.domain.models.user import User
from app.domain.models.store import Store
from app.domain.models.category import Category
from app.domain.models.product import Product
from app.domain.models.product_variant import ProductVariant
from app.domain.models.notification import Notification

# Must match _SEED_USER_ID in security.py so get_current_user returns the store owner.
TEST_USER_ID = uuid.UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")
TEST_STORE_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
TEST_CATEGORY_ID = uuid.UUID("00000000-0000-0000-0000-000000000003")
TEST_PRODUCT_ID = uuid.UUID("00000000-0000-0000-0000-000000000004")
TEST_PRODUCT_2_ID = uuid.UUID("00000000-0000-0000-0000-000000000005")
TEST_VARIANT_1_ID = uuid.UUID("00000000-0000-0000-0000-000000000006")
TEST_VARIANT_2_ID = uuid.UUID("00000000-0000-0000-0000-000000000007")
# Single default variant for TEST_PRODUCT_2 (a one-variant product).
TEST_VARIANT_3_ID = uuid.UUID("00000000-0000-0000-0000-000000000008")
TEST_USER_ID2 = uuid.UUID("00000000-0000-0000-0000-000000000009")
TEST_NOTIFICATION_ID = uuid.UUID("00000000-0000-0000-0000-000000000010")
TEST_NOTIFICATION_ID2 = uuid.UUID("00000000-0000-0000-0000-000000000011")
TEST_NOTIFICATION_ID3 = uuid.UUID("00000000-0000-0000-0000-000000000012")

async def seed_products(db):
    user = User(
        id=TEST_USER_ID, email="test@test.com", password_hash="hash", role="vendor"
    )
    db.add(user)

    user2 = User(
        id=TEST_USER_ID2, email="test2@test.com", password_hash="hash", role="buyer"
    )
    db.add(user2)

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
    db.add(product2)

    variant1 = ProductVariant(
        id=TEST_VARIANT_1_ID,
        product_id=TEST_PRODUCT_ID,
        name="Size",
        value="S",
        price_modifier=Decimal("0.00"),
        stock_quantity=50,
    )

    variant2 = ProductVariant(
        id=TEST_VARIANT_2_ID,
        product_id=TEST_PRODUCT_ID,
        name="Size",
        value="M",
        price_modifier=Decimal("15.00"),
        stock_quantity=50,
    )

    variant3 = ProductVariant(
        id=TEST_VARIANT_3_ID,
        product_id=TEST_PRODUCT_2_ID,
        name="Default",
        value="Único",
        price_modifier=Decimal("0.00"),
        stock_quantity=30,
    )

    db.add(variant1)
    db.add(variant2)
    db.add(variant3)

    notif = Notification(
        id=TEST_NOTIFICATION_ID,
        user_id=TEST_USER_ID,
        title="Test notification",
        body="Test body",
        type="order_confirmed",
        reference_id=uuid.uuid4(),
        is_read=False,
    )

    notif2 = Notification(
        id=TEST_NOTIFICATION_ID2,
        user_id=TEST_USER_ID,
        title="Test notification2",
        body="Test body",
        type="order_confirmed",
        reference_id=uuid.uuid4(),
        is_read=True,
    )

    notif3 = Notification(
        id=TEST_NOTIFICATION_ID3,
        user_id=TEST_USER_ID2,
        title="Test notification3",
        body="Test body",
        type="order_confirmed",
        reference_id=uuid.uuid4(),
        is_read=False,
    )

    db.add(notif)
    db.add(notif2)
    db.add(notif3)

    await db.commit()
    await db.refresh(product)
    return product
