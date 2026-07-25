"""add duration max and activity check constraints

Revision ID: 65d5c7f69308
Revises: ae778bcbbed0
Create Date: 2026-07-25 22:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "65d5c7f69308"
down_revision = "ae778bcbbed0"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("workouts") as batch_op:
        batch_op.create_check_constraint(
            "ck_workouts_duration_max",
            "duration_minutes <= 1440",
        )

    with op.batch_alter_table("workout_exercises") as batch_op:
        batch_op.create_check_constraint(
            "ck_workout_exercises_has_activity",
            "reps > 0 OR sets > 0 OR duration_seconds > 0",
        )


def downgrade():
    with op.batch_alter_table("workout_exercises") as batch_op:
        batch_op.drop_constraint("ck_workout_exercises_has_activity", type_="check")

    with op.batch_alter_table("workouts") as batch_op:
        batch_op.drop_constraint("ck_workouts_duration_max", type_="check")
