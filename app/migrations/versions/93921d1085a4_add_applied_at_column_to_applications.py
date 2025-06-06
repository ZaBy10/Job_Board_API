"""Add applied_at column to applications

Revision ID: 93921d1085a4
Revises: 2cecd8893bd6
Create Date: 2025-03-30 15:23:14.582017

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '93921d1085a4'
down_revision: Union[str, None] = '2cecd8893bd6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    with op.batch_alter_table('applications') as batch_op:
        batch_op.add_column(
            sa.Column('applied_at', 
                sa.DateTime(), 
                server_default=sa.text('CURRENT_TIMESTAMP'),
                nullable=False)
        )

def downgrade():
    op.drop_column('applications', 'applied_at')
