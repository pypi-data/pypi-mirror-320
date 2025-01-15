# -*- coding: utf-8 -*-
"""empty message

Revision ID: roc_dingo_0031_add_sbm_subtype
Revises: roc_dingo_0030_add_packet_acq_time
Create Date: 2024-04-25 10:44:55.787939

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "roc_dingo_0031_add_sbm_subtype"
down_revision = "roc_dingo_0030_add_packet_acq_time"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "sbm_log",
        sa.Column("sbm_subtype", sa.String(), nullable=True),
        schema="pipeline",
    )


def downgrade():
    op.drop_column("sbm_log", "sbm_subtype", schema="pipeline")
