from typing import Optional

from pydantic import BaseModel, field_validator


class Relationship(BaseModel):
    """Model representing a relationship between entities in a domain.

    Contains information about the hierarchy of relationships (parents/children) and inverse relationships.
    """

    name: str
    id: str
    parent_ids: list[str]
    child_ids: list[str]
    inverse_ids: list[str]
    domain_prefix: str

    @field_validator("domain_prefix", mode="before")
    @classmethod
    def extract_domain_prefix(cls, value):
        return value["prefix"] if value else None

    @field_validator("parent_ids", mode="before")
    @classmethod
    def extract_parent_ids(cls, value):
        return [e["id"] for e in value] if value else []

    @field_validator("child_ids", mode="before")
    @classmethod
    def extract_child_ids(cls, value):
        return [e["id"] for e in value] if value else []

    @field_validator("inverse_ids", mode="before")
    @classmethod
    def extract_inverse_ids(cls, value):
        return [value["id"]] if value else []


class Trait(BaseModel):
    """Model representing a trait that can be assigned to entities.

    Contains hierarchical information about parent/child relationships and equivalent traits.
    """

    name: str
    id: str
    domain_prefix: str
    parent_ids: list[str]
    child_ids: list[str]
    equivalent_ids: list[str]

    @field_validator("domain_prefix", mode="before")
    @classmethod
    def extract_domain_prefix(cls, value):
        return value["prefix"] if value else None

    @field_validator("parent_ids", mode="before")
    @classmethod
    def extract_parent_ids(cls, value):
        return [e["id"] for e in value] if value else []

    @field_validator("child_ids", mode="before")
    @classmethod
    def extract_child_ids(cls, value):
        return [e["id"] for e in value] if value else []

    @field_validator("equivalent_ids", mode="before")
    @classmethod
    def extract_equivalent_ids(cls, value):
        return [e["id"] for e in value] if value else []


class Domain(BaseModel):
    """Model representing a domain containing traits and relationships.

    A domain defines a namespace of traits and relationships that can be used to describe entities.
    """

    name: str
    prefix: str
    description: Optional[str]
    uri: str
    traits: list[Trait]
    relationships: list[Relationship]

    @field_validator("traits", mode="before")
    @classmethod
    def validate_traits(cls, value):
        return value if value else []

    @field_validator("relationships", mode="before")
    @classmethod
    def validate_relationships(cls, value):
        return value if value else []

    def __init__(self, **data):
        super().__init__(**data)
        self._trait_dict = (
            {trait.id: trait for trait in self.traits} if self.traits else {}
        )

    def get_trait_by_id(self, id: str) -> Trait:
        """Returns mapping of trait IDs to Trait objects."""
        return self._trait_dict[id]
