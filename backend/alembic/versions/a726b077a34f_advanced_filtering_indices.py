"""advanced_filtering_indices

Revision ID: a726b077a34f
Revises: 7900d6512df1
Create Date: 2026-08-19 16:10:49.293114

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'a726b077a34f'
down_revision: Union[str, None] = '7900d6512df1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('idx_issues_status', 'issues', ['status'])
    op.create_index('idx_issues_type', 'issues', ['issue_type'])
    op.create_index('idx_issues_location_id', 'issues', ['location_id'])
    op.create_index('idx_issues_created_at', 'issues', [sa.text('created_at DESC')])
    op.create_index('idx_issues_created_by', 'issues', ['created_by'])
    op.create_index('idx_issue_comments_issue_id', 'issue_comments', ['issue_id'])
    op.create_index('idx_issue_assignments_issue_id', 'issue_assignments', ['issue_id'])
    op.create_index('idx_issue_assignments_contractor_id', 'issue_assignments', ['contractor_id'])
    
    op.execute("CREATE INDEX idx_issues_title_fts ON issues USING GIN(to_tsvector('english', coalesce(title, '')));")
    op.execute("CREATE INDEX idx_issues_description_fts ON issues USING GIN(to_tsvector('english', coalesce(description, '')));")
    op.execute("CREATE INDEX idx_comments_content_fts ON issue_comments USING GIN(to_tsvector('english', coalesce(comment_text, '')));")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_comments_content_fts;")
    op.execute("DROP INDEX IF EXISTS idx_issues_description_fts;")
    op.execute("DROP INDEX IF EXISTS idx_issues_title_fts;")
    
    op.drop_index('idx_issue_assignments_contractor_id', table_name='issue_assignments')
    op.drop_index('idx_issue_assignments_issue_id', table_name='issue_assignments')
    op.drop_index('idx_issue_comments_issue_id', table_name='issue_comments')
    op.drop_index('idx_issues_created_by', table_name='issues')
    op.drop_index('idx_issues_created_at', table_name='issues')
    op.drop_index('idx_issues_location_id', table_name='issues')
    op.drop_index('idx_issues_type', table_name='issues')
    op.drop_index('idx_issues_status', table_name='issues')
