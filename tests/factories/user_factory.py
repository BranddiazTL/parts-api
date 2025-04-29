import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker

from app.models.user import User, UserRole
from app.services.security_service import get_password_hash

fake = Faker()


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "flush"

    email = factory.LazyFunction(fake.email)
    username = factory.LazyFunction(lambda: fake.user_name()[:50])
    is_active = True
    role = UserRole.MEMBER
    is_superuser = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override create and hash password."""
        if "session" not in kwargs:
            raise RuntimeError("SQLAlchemy session must be provided to UserFactory")

        session = kwargs.pop("session")
        cls._meta.sqlalchemy_session = session

        raw_password = kwargs.pop("password", "testpassword123")
        kwargs["password"] = get_password_hash(raw_password)

        if kwargs.pop("is_superuser", False):
            kwargs["role"] = UserRole.ADMIN
        elif "role" not in kwargs:
            kwargs["role"] = cls.role

        instance = super()._create(model_class, *args, **kwargs)

        return instance
