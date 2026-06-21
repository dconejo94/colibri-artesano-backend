from pydantic import BaseModel, model_validator
from uuid import UUID
from decimal import Decimal
from typing import Any


class ProductAutocompleteDTO(BaseModel):
    """Lightweight projection returned by the autocomplete endpoint.

    Deliberately minimal: id, name, price and a single cover image URL are
    everything a search-as-you-type widget needs.  The primary image is
    resolved from the eagerly-loaded ``images`` relationship; if no image is
    marked primary the first available image is used.
    """

    id: UUID
    name: str
    base_price: Decimal
    primary_image_url: str | None = None

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def _extract_primary_image(cls, data: Any) -> Any:
        """Pull the cover image URL out of the ORM relationship before
        Pydantic tries to serialise the object."""
        if isinstance(data, dict):
            return data

        result = {
            "id": getattr(data, "id", None),
            "name": getattr(data, "name", None),
            "base_price": getattr(data, "base_price", None),
            "primary_image_url": None,
        }

        # Images live on variants now; the cover comes from the first variant
        # (lowest id) — its primary image, or the first available one.
        variants = getattr(data, "variants", None) or []
        if variants:
            first_variant = min(variants, key=lambda v: str(v.id))
            images = getattr(first_variant, "images", None) or []
            if images:
                primary = next(
                    (img for img in images if getattr(img, "is_primary", False)),
                    images[0],
                )
                result["primary_image_url"] = primary.image_url

        return result
