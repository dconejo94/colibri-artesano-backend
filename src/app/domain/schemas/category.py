from pydantic import BaseModel
from uuid import UUID


class CategoryCreateDTO(BaseModel):
    name: str
    slug: str


class CategoryUpdateDTO(BaseModel):
    name: str | None = None
    slug: str | None = None


class CategoryResponseDTO(BaseModel):
    id: UUID
    name: str
    slug: str

    model_config = {"from_attributes": True}


class CategoryAutocompleteDTO(BaseModel):
    id: UUID
    name: str
    slug: str

    model_config = {"from_attributes": True}
