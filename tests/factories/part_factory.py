import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
import random

from app.models.part import Part, PartVisibility

fake = Faker()


class PartFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Part
        sqlalchemy_session_persistence = "flush"

    name = factory.LazyFunction(lambda: f"Part {fake.word()} {fake.word()}")
    sku = factory.LazyFunction(
        lambda: f"SKU-{random.randint(1000, 9999)}-{fake.lexify('????').upper()}"
    )
    description = factory.LazyFunction(fake.sentence)
    weight_ounces = factory.LazyFunction(lambda: random.randint(1, 100))
    is_active = True
    visibility = factory.LazyFunction(lambda: random.choice(list(PartVisibility)))
    owner_id = None

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        if "session" not in kwargs:
            raise RuntimeError("SQLAlchemy session must be provided to PartFactory")
        session = kwargs.pop("session")
        cls._meta.sqlalchemy_session = session  # Set session for base class

        if "owner" in kwargs:
            owner = kwargs.pop("owner")
            kwargs["owner_id"] = str(owner.id)
        elif "owner_id" not in kwargs or kwargs["owner_id"] is None:
            raise RuntimeError("owner or owner_id must be provided to PartFactory")

        instance = super()._create(model_class, *args, **kwargs)

        return instance
