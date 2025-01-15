"""empty message

Revision ID: roc_dingo_0029_tm_log_partitioning
Revises: roc_dingo_0028_modify_sbm_log_status_retrieved
Create Date: 2023-11-02 19:14:28.193974

"""

from pathlib import Path

from alembic import op

from poppy.pop.alembic.helpers import execute, user

# revision identifiers, used by Alembic.
revision = "roc_dingo_0029_tm_log_partitioning"
down_revision = "roc_dingo_0028_modify_sbm_log_status_retrieved"
branch_labels = None
depends_on = None


def upgrade():
    # This command works
    filename = "SQL/roc_dingo_0029__upgrade.sql"
    sql_file = Path(__file__).parent / filename
    with open(sql_file, "r") as sql_content:
        sql_cmd = sql_content.read()
        op.execute(sql_cmd)

    # added by hand
    # fix table permissions
    grant_user_perm = """GRANT SELECT, INSERT, UPDATE
        ON ALL TABLES IN SCHEMA pipeline TO {0}""".format(user)
    execute(grant_user_perm)
    # fix truncate table permissions
    # (required when running event_to_db task with --force option)
    grant_user_truncate = """GRANT TRUNCATE
        ON TABLE pipeline.event_log TO {0}""".format(user)
    execute(grant_user_truncate)
    # Make sure user can reset event_log_id_seq
    # alter_seq_user = (
    #    """ALTER SEQUENCE IF EXISTS event_log_id_seq
    #    OWNER TO {0}""".format(user)
    # )
    # execute(alter_seq_user)
    # fix sequence permissions
    grant_user_seq = """GRANT USAGE, SELECT
        ON ALL SEQUENCES IN SCHEMA pipeline TO {0}""".format(user)
    execute(grant_user_seq)


def downgrade():
    # This command works
    filename = "SQL/roc_dingo_0029__downgrade.sql"
    sql_file = Path(__file__).parent / filename
    with open(sql_file, "r") as sql_content:
        sql_cmd = sql_content.read()
        op.execute(sql_cmd)

    # added by hand
    # fix table permissions
    grant_user_perm = """GRANT SELECT, INSERT, UPDATE
        ON ALL TABLES IN SCHEMA pipeline TO {0}""".format(user)
    execute(grant_user_perm)
    # Make sure admin can reset event_log_id_seq
    # alter_seq_admin = (
    #    """ALTER SEQUENCE IF EXISTS event_log_id_seq
    #    OWNER TO {0}""".format(admin)
    # )
    # execute(alter_seq_admin)
    # Fix sequence permissions
    grant_user_seq = """GRANT USAGE, SELECT
        ON ALL SEQUENCES IN SCHEMA pipeline TO {0}""".format(user)
    execute(grant_user_seq)
