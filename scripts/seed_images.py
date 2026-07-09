"""Generate and upload a real placeholder image for every product variant
that doesn't have one yet, using the actual Azurite blob storage backing the
app (not a hardcoded external URL). Run after `alembic upgrade head` +
`scripts/seed.sql`, from inside the backend container so `db`/`azurite`
resolve as docker-compose service hostnames:

    docker exec colibri-backend uv run python scripts/seed_images.py
"""

import hashlib
import io
import uuid

import psycopg
from azure.storage.blob import BlobServiceClient, PublicAccess
from PIL import Image, ImageDraw, ImageFont

from app.config import settings

# A handful of brand-consistent accent colors (from src/theme/colors.ts on the
# mobile side) so generated covers don't all look identical.
PALETTE = ["#8CBF9B", "#B58E5A", "#6FA882", "#5E9C9C", "#9B7BC4", "#CD6B60", "#4A7C59"]

# Connects from *inside* the backend container via the docker-compose service
# name — independent of AZURE_STORAGE_BLOB_ENDPOINT, which is a LAN IP meant
# for external clients (the mobile app), not container-to-container traffic.
_INTERNAL_CONN_STR = (
    "DefaultEndpointsProtocol=http;"
    f"AccountName={settings.AZURE_STORAGE_ACCOUNT_NAME};"
    f"AccountKey={settings.AZURE_STORAGE_ACCOUNT_KEY};"
    f"BlobEndpoint=http://azurite:10000/{settings.AZURE_STORAGE_ACCOUNT_NAME};"
)


def _color_for(seed: str) -> str:
    digest = int(hashlib.sha1(seed.encode()).hexdigest(), 16)
    return PALETTE[digest % len(PALETTE)]


def _wrap(text: str, max_chars: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if len(trial) > max_chars and current:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines


def _load_font(size: int) -> ImageFont.ImageFont:
    for candidate in ("DejaVuSans-Bold.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def generate_image(title: str, subtitle: str, seed: str) -> bytes:
    size = 640
    img = Image.new("RGB", (size, size), color=_color_for(seed))
    draw = ImageDraw.Draw(img)
    title_font = _load_font(40)
    subtitle_font = _load_font(28)

    lines = _wrap(title, 16)
    total_height = len(lines) * 48 + (36 if subtitle else 0)
    y = (size - total_height) / 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        w = bbox[2] - bbox[0]
        draw.text(((size - w) / 2, y), line, font=title_font, fill="white")
        y += 48

    if subtitle:
        bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        w = bbox[2] - bbox[0]
        draw.text(((size - w) / 2, y + 8), subtitle, font=subtitle_font, fill="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def main() -> None:
    if not settings.AZURE_STORAGE_CONFIGURED:
        print(
            "Azure storage is not configured (AZURE_STORAGE_ACCOUNT_NAME/KEY blank) — aborting."
        )
        return

    blob_service = BlobServiceClient.from_connection_string(_INTERNAL_CONN_STR)
    container = blob_service.get_container_client(settings.AZURE_STORAGE_CONTAINER)
    if not container.exists():
        container.create_container()
    # Anonymous read access for blobs — the mobile app loads image_url
    # directly with no auth, same as it would against real Azure with a
    # public container.
    container.set_container_access_policy(
        signed_identifiers={}, public_access=PublicAccess.BLOB
    )

    conn = psycopg.connect(
        host="db",
        port=5432,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        dbname=settings.POSTGRES_DB,
    )
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(
        """
        SELECT v.id, v.name, v.value, p.name
        FROM product_variants v
        JOIN products p ON p.id = v.product_id
        WHERE NOT EXISTS (SELECT 1 FROM product_images pi WHERE pi.variant_id = v.id)
        ORDER BY p.name, v.name
        """
    )
    rows = cur.fetchall()
    print(f"{len(rows)} variant(s) without an image.")

    base_url = settings.AZURE_BLOB_BASE_URL  # LAN-IP based — usable by the mobile app

    for variant_id, variant_name, variant_value, product_name in rows:
        subtitle = (
            "" if variant_value == "Único" else f"{variant_name}: {variant_value}"
        )
        image_bytes = generate_image(product_name, subtitle, str(variant_id))

        blob_name = f"{variant_id}/{uuid.uuid4().hex}.png"
        container.upload_blob(
            blob_name, image_bytes, overwrite=True, content_type="image/png"
        )
        image_url = f"{base_url}/{settings.AZURE_STORAGE_CONTAINER}/{blob_name}"

        cur.execute(
            "INSERT INTO product_images (id, variant_id, image_url, is_primary) VALUES (%s, %s, %s, true)",
            (str(uuid.uuid4()), str(variant_id), image_url),
        )
        print(f"  {product_name} ({subtitle or 'Único'}) -> {image_url}")

    cur.close()
    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()
