"""init

Revision ID: 3fb8eedaf198
Revises: 
Create Date: 2024-07-12 17:42:11.020575

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3fb8eedaf198'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('enterprise_for_research',
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('uuid'),
    sa.UniqueConstraint('name')
    )
    op.create_table('vetis_user',
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('login', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('uuid'),
    sa.UniqueConstraint('login')
    )
    op.create_table('base_research',
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('sampling_number', sa.String(), nullable=True),
    sa.Column('sampling_date', sa.String(), nullable=True),
    sa.Column('operator', sa.String(), nullable=False),
    sa.Column('disease', sa.String(), nullable=False),
    sa.Column('date_of_research', sa.String(), nullable=False),
    sa.Column('method', sa.String(), nullable=False),
    sa.Column('expertise_id', sa.String(), nullable=False),
    sa.Column('result', sa.String(), nullable=False),
    sa.Column('conclusion', sa.String(), nullable=False),
    sa.Column('enterprise_uuid', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['enterprise_uuid'], ['enterprise_for_research.uuid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_table('exclude_products',
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('product', sa.String(), nullable=False),
    sa.Column('enterprise_uuid', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['enterprise_uuid'], ['enterprise_for_research.uuid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_table('special_research',
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('product', sa.String(), nullable=False),
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
    sa.ForeignKeyConstraint(['enterprise_uuid'], ['enterprise_for_research.uuid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('uuid')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('special_research')
    op.drop_table('exclude_products')
    op.drop_table('base_research')
    op.drop_table('vetis_user')
    op.drop_table('enterprise_for_research')
    # ### end Alembic commands ###
