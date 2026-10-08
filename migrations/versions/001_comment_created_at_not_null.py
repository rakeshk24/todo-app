"""Backfill comment timestamps before requiring them."""

from alembic import op
import sqlalchemy as sa


revision = '001_comment_created_at_not_null'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    comments = sa.table('comment', sa.column('created_at', sa.DateTime()))
    op.execute(
        comments.update().where(comments.c.created_at.is_(None)).values(
            created_at=sa.func.current_timestamp()
        )
    )
    with op.batch_alter_table('comment') as batch_op:
        batch_op.alter_column('created_at', existing_type=sa.DateTime(), nullable=False)


def downgrade():
    with op.batch_alter_table('comment') as batch_op:
        batch_op.alter_column('created_at', existing_type=sa.DateTime(), nullable=True)
