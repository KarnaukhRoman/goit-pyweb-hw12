"""Add table roles

Revision ID: 93cbb0ac6794
Revises: c3608e60be37
Create Date: 2024-07-31 15:08:48.532898

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.database.models import Role
from src.schemas.roles import RoleEnum

# revision identifiers, used by Alembic.
revision: str = '93cbb0ac6794'
down_revision: Union[str, None] = 'c3608e60be37'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)
    op.add_column('users', sa.Column('role_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'users', 'roles', ['role_id'], ['id'])
    # ### end Alembic commands ###

    op.bulk_insert(Role.__table__,
        [
            {'id': 1, 'name': RoleEnum.admin},
            {'id': 2, 'name': RoleEnum.moderator},
            {'id': 3, 'name': RoleEnum.user},
        ]
    )


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_column('users', 'role_id')
    op.drop_index(op.f('ix_roles_id'), table_name='roles')
    op.drop_table('roles')
    # ### end Alembic commands ###
