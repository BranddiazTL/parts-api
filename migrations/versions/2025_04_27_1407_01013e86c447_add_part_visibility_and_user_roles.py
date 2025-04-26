"""add part visibility and user roles

Revision ID: 01013e86c447
Revises: 6d1b4ce506d6
Create Date: 2025-04-27 14:07:13.436551+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '01013e86c447'
down_revision: Union[str, None] = '6d1b4ce506d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('part_collaborator',
    sa.Column('part_id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('permission', sa.Enum('READ', 'EDIT', name='collaboratorpermission', native_enum=False), nullable=False),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['part_id'], ['part.id'], name='fk_partcollaborator_part_id'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fk_partcollaborator_user_id'),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('part', sa.Column('visibility', sa.Enum('PRIVATE', 'PUBLIC', name='partvisibility', native_enum=False), nullable=False))
    op.add_column('part', sa.Column('owner_id', sa.UUID(), nullable=False))
    op.add_column('user',
                  sa.Column('role', sa.Enum('MEMBER', 'ADMIN', name='userrole', native_enum=False), nullable=False))
    op.create_foreign_key('fk_part_owner_id', 'part', 'user', ['owner_id'], ['id'])

    # Fix manually added indexes naming format
    op.drop_index('idx_part_is_active', table_name='part')
    op.drop_index('idx_part_name', table_name='part')
    op.drop_index('idx_user_is_active', table_name='user')

    op.create_index(op.f('ix_part_is_active'), 'part', ['is_active'], unique=False)
    op.create_index(op.f('ix_part_name'), 'part', ['name'], unique=False)
    op.create_index(op.f('ix_part_owner_id'), 'part', ['owner_id'], unique=False)
    op.create_index(op.f('ix_part_visibility'), 'part', ['visibility'], unique=False)
    op.create_index(op.f('ix_user_is_active'), 'user', ['is_active'], unique=False)
    op.create_index(op.f('ix_user_role'), 'user', ['role'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_user_role'), table_name='user')
    op.drop_index(op.f('ix_user_is_active'), table_name='user')
    op.create_index('idx_user_is_active', 'user', ['is_active'], unique=False)
    op.drop_column('user', 'role')
    op.drop_constraint('fk_part_owner_id', 'part', type_='foreignkey')
    op.drop_index(op.f('ix_part_visibility'), table_name='part')
    op.drop_index(op.f('ix_part_owner_id'), table_name='part')
    op.drop_index(op.f('ix_part_name'), table_name='part')
    op.drop_index(op.f('ix_part_is_active'), table_name='part')
    op.create_index('idx_part_name', 'part', ['name'], unique=False)
    op.create_index('idx_part_is_active', 'part', ['is_active'], unique=False)
    op.drop_column('part', 'owner_id')
    op.drop_column('part', 'visibility')
    op.drop_table('part_collaborator')
