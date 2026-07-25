from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
from marshmallow import Schema, fields, validate, validates as ma_validates, ValidationError

db = SQLAlchemy()

VALID_CATEGORIES = ("Strength", "Cardio", "Flexibility", "Balance")


class Exercise(db.Model, SerializerMixin):
    __tablename__ = "exercises"
    __table_args__ = (
        db.CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_exercises_name_not_blank",
        ),
        db.CheckConstraint(
            "category IN ('Strength', 'Cardio', 'Flexibility', 'Balance')",
            name="ck_exercises_valid_category",
        ),
    )

    serialize_rules = ("-workout_exercises.exercise",)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="exercise",
        cascade="all, delete-orphan",
    )
    workouts = association_proxy("workout_exercises", "workout")

    @validates("name")
    def validate_name(self, key, name):
        if not name or not str(name).strip():
            raise ValueError("Exercise name must be a non-empty string")
        return str(name).strip()

    @validates("category")
    def validate_category(self, key, category):
        if category not in VALID_CATEGORIES:
            raise ValueError(
                f"Category must be one of: {', '.join(VALID_CATEGORIES)}"
            )
        return category

    @validates("equipment_needed")
    def validate_equipment_needed(self, key, equipment_needed):
        if not isinstance(equipment_needed, bool):
            raise ValueError("equipment_needed must be a boolean")
        return equipment_needed

    def __repr__(self):
        return f"<Exercise {self.id}: {self.name}>"


class Workout(db.Model, SerializerMixin):
    __tablename__ = "workouts"
    __table_args__ = (
        db.CheckConstraint(
            "duration_minutes > 0",
            name="ck_workouts_duration_positive",
        ),
    )

    serialize_rules = ("-workout_exercises.workout",)

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",
    )
    exercises = association_proxy("workout_exercises", "exercise")

    @validates("date")
    def validate_date(self, key, date):
        if date is None:
            raise ValueError("Workout date is required")
        return date

    @validates("duration_minutes")
    def validate_duration_minutes(self, key, duration_minutes):
        if duration_minutes is None or not isinstance(duration_minutes, int):
            raise ValueError("duration_minutes must be an integer")
        if duration_minutes <= 0:
            raise ValueError("duration_minutes must be greater than 0")
        return duration_minutes

    def __repr__(self):
        return f"<Workout {self.id}: {self.date}>"


class WorkoutExercise(db.Model, SerializerMixin):
    __tablename__ = "workout_exercises"
    __table_args__ = (
        db.UniqueConstraint(
            "workout_id",
            "exercise_id",
            name="uq_workout_exercise_pair",
        ),
        db.CheckConstraint("reps >= 0", name="ck_workout_exercises_reps_nonneg"),
        db.CheckConstraint("sets >= 0", name="ck_workout_exercises_sets_nonneg"),
        db.CheckConstraint(
            "duration_seconds >= 0",
            name="ck_workout_exercises_duration_nonneg",
        ),
    )

    serialize_rules = (
        "-workout.workout_exercises",
        "-exercise.workout_exercises",
    )

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(
        db.Integer,
        db.ForeignKey("workouts.id", ondelete="CASCADE"),
        nullable=False,
    )
    exercise_id = db.Column(
        db.Integer,
        db.ForeignKey("exercises.id", ondelete="CASCADE"),
        nullable=False,
    )
    reps = db.Column(db.Integer, nullable=False, default=0)
    sets = db.Column(db.Integer, nullable=False, default=0)
    duration_seconds = db.Column(db.Integer, nullable=False, default=0)

    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    @validates("reps", "sets", "duration_seconds")
    def validate_non_negative(self, key, value):
        if value is None or not isinstance(value, int):
            raise ValueError(f"{key} must be an integer")
        if value < 0:
            raise ValueError(f"{key} must be greater than or equal to 0")
        return value

    def __repr__(self):
        return (
            f"<WorkoutExercise workout={self.workout_id} "
            f"exercise={self.exercise_id}>"
        )


# ---------- Marshmallow Schemas (schema-level validations) ----------


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
    )
    category = fields.Str(
        required=True,
        validate=validate.OneOf(VALID_CATEGORIES),
    )
    equipment_needed = fields.Bool(required=True)

    @ma_validates("name")
    def validate_name_not_blank(self, value, **kwargs):
        if not value or not value.strip():
            raise ValidationError("Name cannot be blank")


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(
        required=True,
        validate=validate.Range(min=1, error="duration_minutes must be at least 1"),
    )
    notes = fields.Str(allow_none=True, load_default=None)

    @ma_validates("notes")
    def validate_notes_length(self, value, **kwargs):
        if value is not None and len(value) > 1000:
            raise ValidationError("Notes cannot exceed 1000 characters")


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(
        required=True,
        validate=validate.Range(min=0),
    )
    sets = fields.Int(
        required=True,
        validate=validate.Range(min=0),
    )
    duration_seconds = fields.Int(
        required=True,
        validate=validate.Range(min=0),
    )

    @ma_validates("reps")
    def validate_reps_integer(self, value, **kwargs):
        if value is None:
            raise ValidationError("reps is required")


exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
workout_exercise_schema = WorkoutExerciseSchema()
