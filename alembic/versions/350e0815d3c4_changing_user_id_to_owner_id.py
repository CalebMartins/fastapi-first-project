"""changing user_id to owner_id

Revision ID: 350e0815d3c4
Revises: 029ee08a267e
Create Date: 2024-11-12 10:33:07.430470

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '350e0815d3c4'
down_revision: Union[str, None] = '029ee08a267e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('owner_id', sa.Integer(), nullable=True))
    
    # Populate `owner_id` with values from `user_id` or a default value
    op.execute('UPDATE posts SET owner_id = user_id WHERE owner_id IS NULL')
    
    # Now set `owner_id` to NOT NULL
    op.alter_column('posts', 'owner_id', nullable=False)

    # Drop the old foreign key and column
    op.drop_constraint('fk_posts_user_id', 'posts', type_='foreignkey')
    op.create_foreign_key(None, 'posts', 'users', ['owner_id'], ['id'], ondelete='CASCADE')
    op.drop_column('posts', 'user_id')
    # ### end Alembic commands ###



def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'posts', type_='foreignkey')
    op.create_foreign_key('fk_posts_user_id', 'posts', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_column('posts', 'owner_id')
    # ### end Alembic commands ###
