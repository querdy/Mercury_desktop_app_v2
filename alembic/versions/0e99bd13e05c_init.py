"""init

Revision ID: 0e99bd13e05c
Revises: 
Create Date: 2024-09-07 23:32:04.164081

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e99bd13e05c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('enterprise',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('pk', sa.String(), nullable=False),
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.PrimaryKeyConstraint('uuid'),
    sa.UniqueConstraint('name')
    )
    op.create_table('vetis_user',
    sa.Column('login', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.PrimaryKeyConstraint('uuid'),
    sa.UniqueConstraint('login')
    )
    op.create_table('exclude_products',
    sa.Column('product', sa.String(), nullable=False),
    sa.Column('enterprise_uuid', sa.UUID(), nullable=False),
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['enterprise_uuid'], ['enterprise.uuid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_table('immunization',
    sa.Column('product', sa.String(), nullable=True),
    sa.Column('operation_type', sa.String(), nullable=False),
    sa.Column('illness', sa.String(), nullable=False),
    sa.Column('operation_date', sa.String(), nullable=False),
    sa.Column('vaccine_name', sa.String(), nullable=True),
    sa.Column('vaccine_serial', sa.String(), nullable=True),
    sa.Column('vaccine_date_to', sa.String(), nullable=True),
    sa.Column('enterprise_uuid', sa.UUID(), nullable=False),
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['enterprise_uuid'], ['enterprise.uuid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_table('research',
    sa.Column('product', sa.String(), nullable=True),
    sa.Column('sampling_number', sa.String(), nullable=True),
    sa.Column('sampling_date', sa.String(), nullable=True),
    sa.Column('operator', sa.String(), nullable=False),
    sa.Column('disease', sa.String(), nullable=False),
    sa.Column('date_of_research', sa.String(), nullable=False),
    sa.Column('method', sa.String(), nullable=True),
    sa.Column('expertise_id', sa.String(), nullable=False),
    sa.Column('result', sa.String(), nullable=False),
    sa.Column('conclusion', sa.String(), nullable=False),
    sa.Column('enterprise_uuid', sa.UUID(), nullable=False),
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['enterprise_uuid'], ['enterprise.uuid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('uuid')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('research')
    op.drop_table('immunization')
    op.drop_table('exclude_products')
    op.drop_table('vetis_user')
    op.drop_table('enterprise')
    # ### end Alembic commands ###
