import uuid

# El usuario de seed es creado por product_factory.seed_products.
# Esta constante existe para que los tests de usuario puedan referenciarlo sin
# importar desde product_factory.
TEST_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
