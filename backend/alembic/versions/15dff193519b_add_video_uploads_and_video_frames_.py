"""add video_uploads and video_frames tables

Revision ID: 15dff193519b
Revises: a726b077a34f
Create Date: 2026-09-06 11:04:24.174572

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '15dff193519b'
down_revision: Union[str, None] = 'a726b077a34f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # video_uploads table
    op.create_table(
        'video_uploads',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('path_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('fps', sa.Integer(), nullable=True),
        sa.Column('resolution', sa.String(length=50), nullable=True),
        sa.Column('codec', sa.String(length=50), nullable=True),
        sa.Column('gcs_url', sa.String(length=500), nullable=True),
        sa.Column('upload_status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['path_id'], ['paths.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # video_frames table
    op.create_table(
        'video_frames',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('video_id', sa.String(), nullable=False),
        sa.Column('frame_number', sa.Integer(), nullable=False),
        sa.Column('timestamp_seconds', sa.Float(), nullable=False),
        sa.Column('thumbnail_url', sa.String(length=500), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['video_id'], ['video_uploads.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Indices
    op.create_index('idx_video_uploads_path_id', 'video_uploads', ['path_id'])
    op.create_index('idx_video_uploads_user_id', 'video_uploads', ['user_id'])
    op.create_index('idx_video_frames_video_id', 'video_frames', ['video_id'])


def downgrade() -> None:
    op.drop_index('idx_video_frames_video_id', table_name='video_frames')
    op.drop_index('idx_video_uploads_user_id', table_name='video_uploads')
    op.drop_index('idx_video_uploads_path_id', table_name='video_uploads')
    op.drop_table('video_frames')
    op.drop_table('video_uploads')
