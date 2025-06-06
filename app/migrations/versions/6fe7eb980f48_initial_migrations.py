"""Initial migrations

Revision ID: 6fe7eb980f48
Revises: 
Create Date: 2025-03-30 15:11:36.825863

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '6fe7eb980f48'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('applications') as batch_op:
        # Fix applicant_id nullability
        batch_op.alter_column('applicant_id', nullable=True)
        
        # Convert status to ENUM
        batch_op.alter_column('status',
               existing_type=sa.VARCHAR(length=14),
               type_=sa.Enum('SELECTED', 'REJECTED', 'UNDER_REVIEW', name='status'),
               existing_nullable=True)

def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('applications') as batch_op:
        # Revert status to VARCHAR
        batch_op.alter_column('status',
               existing_type=sa.Enum('SELECTED', 'REJECTED', 'UNDER_REVIEW', name='status'),
               type_=sa.VARCHAR(length=14),
               existing_nullable=True)
        
        # Restore applicant_id non-nullable
        batch_op.alter_column('applicant_id', nullable=False)