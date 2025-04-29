from enum import StrEnum

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class PartVisibility(StrEnum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"


class CollaboratorPermission(StrEnum):
    READ = "READ"
    EDIT = "EDIT"


class Part(Base):
    __tablename__ = "part"
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    sku: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(1024))
    weight_ounces: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    visibility: Mapped[PartVisibility] = mapped_column(
        Enum(PartVisibility, native_enum=False),
        default=PartVisibility.PUBLIC,
        nullable=False,
        index=True,
    )
    owner_id: Mapped[str] = mapped_column(
        ForeignKey("user.id", name="fk_part_owner_id"), nullable=False, index=True
    )


class PartCollaborator(Base):
    __tablename__ = "part_collaborator"
    part_id: Mapped[str] = mapped_column(
        ForeignKey("part.id", name="fk_partcollaborator_part_id"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("user.id", name="fk_partcollaborator_user_id"), nullable=False
    )
    permission: Mapped[CollaboratorPermission] = mapped_column(
        Enum(CollaboratorPermission, native_enum=False),
        default=CollaboratorPermission.READ,
        nullable=False,
    )
