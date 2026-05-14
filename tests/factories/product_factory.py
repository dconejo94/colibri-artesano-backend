from app.domain.models.product import Product


def seed_products(db):
    product = Product(
        id=1,
        store_id=1,
        name="Artesania",
        description="Lorem Ipsum",
        price=10,
        stock=5,
        image_url=None,
        category="artesania",
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product
