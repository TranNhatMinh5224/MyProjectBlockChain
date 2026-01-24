"""seed_ministry

Revision ID: 2360237e22bf
Revises: 778529d91b47
Create Date: 2026-01-22 04:01:56.666093

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = '2360237e22bf'
down_revision: Union[str, Sequence[str], None] = '778529d91b47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Seed Ministry Data and Roles."""
    
    # --- MINISTRY CREDENTIALS (DEVELOPMENT/LEARNING) ---
    # Email: admin@moet.gov.vn
    # Password: MinistryPassword123!@#
    # Private Key: (See bottom)
    # ---------------------------------------------------

    # 1. Insert Roles (Standard ADMIN/USER to match Enum)
    op.execute(text("INSERT INTO roles (id, name, created_at) VALUES (1, 'ADMIN', NOW()) ON CONFLICT (id) DO NOTHING"))
    op.execute(text("INSERT INTO roles (id, name, created_at) VALUES (2, 'USER', NOW()) ON CONFLICT (id) DO NOTHING"))
    
    # 2. Reset & Insert Ministry User
    op.execute(text("DELETE FROM users WHERE username = 'admin'"))
    
    # role_name='MINISTRY' to keep business logic working, but role_id=1 (ADMIN)
    op.execute(text(
        "INSERT INTO users (username, email, password_hash, full_name, role_id, role_name, status, created_at) "
        "VALUES ('admin', 'admin@moet.gov.vn', '$2b$12$ECfyMfTAaAA9KCiaRlVElOQNraY2RrivwSQ0echCKRts3oZeymFVq', "
        "'Ministry of Education and Training', 1, 'MINISTRY', 'ACTIVE', NOW())"
    ))

    # 3. Reset & Insert Ministry Config
    # Correct Schema: id, public_key, initialized, created_at
    op.execute(text("DELETE FROM ministry_config"))
    
    # Public Key Formatted for Backend (0xX,0xY)
    # Original: 0446a6c794d4f3e7305c25ca3bc23e9a5e62e07b10e037b40d566e27c1dfa96f95875f60f13acda400569b5b985d569336aa4c54d5d7c23a0de838565ad7c48720
    # X: 46a6c794d4f3e7305c25ca3bc23e9a5e62e07b10e037b40d566e27c1dfa96f
    # Y: 95875f60f13acda400569b5b985d569336aa4c54d5d7c23a0de838565ad7c48720
    
    pub_key = '0x46a6c794d4f3e7305c25ca3bc23e9a5e62e07b10e037b40d566e27c1dfa96f,0x95875f60f13acda400569b5b985d569336aa4c54d5d7c23a0de838565ad7c48720'
    
    op.execute(text(
        f"INSERT INTO ministry_config (public_key, initialized, created_at) "
        f"VALUES ('{pub_key}', true, NOW())"
    ))
    
    # --- PRIVATE KEY COMMENT (FOR USER INFO) ---
    # Private Key (Hex): 6bc0ca494085a2f5655882b4e67094170dc8ccd9a2647e2ef85b5749131bb66b


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(text("DELETE FROM ministry_config"))
    op.execute(text("DELETE FROM users WHERE username = 'admin'"))
    op.execute(text("DELETE FROM roles WHERE id IN (1, 2)"))
