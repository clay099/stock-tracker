"""Initial migration.

Revision ID: e5ee26f50c5b
Revises: 
Create Date: 2020-07-15 13:48:21.946692

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e5ee26f50c5b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('stock_details')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stock_details',
    sa.Column('country', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('currency', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('exchange', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('ipo', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('marketCapitalization', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('phone', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('shareOutstanding', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('ticker', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('weburl', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('logo', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('finnhubIndustry', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('ticker', name='stock_details_pkey')
    )
    # ### end Alembic commands ###
