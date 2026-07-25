from marshmallow import fields, validate, validates, validates_schema, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from models import db, Exercise, Workout, WorkoutExercise, VALID_CATEGORIES


class ExerciseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Exercise
        load_instance = True
        sqla_session = db.session
        include_fk = True

    id = fields.Integer(dump_only=True)
    name = fields.String(
        required=True,
        validate=[
            validate.Length(min=1, max=100),
            validate.Regexp(r".*\S.*", error="Name cannot be blank"),
        ],
    )
    category = fields.String(
        required=True,
        validate=validate.OneOf(
            VALID_CATEGORIES,
            error=f"Category must be one of: {', '.join(VALID_CATEGORIES)}",
        ),
    )
    equipment_needed = fields.Boolean(required=True)

    @validates("name")
    def validate_name_not_blank(self, value, **kwargs):
        if not value or not value.strip():
            raise ValidationError("Name cannot be blank")
        if len(value.strip()) > 100:
            raise ValidationError("Name cannot exceed 100 characters")


class WorkoutSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Workout
        load_instance = True
        sqla_session = db.session
        include_fk = True

    id = fields.Integer(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Integer(
        required=True,
        validate=validate.Range(
            min=1,
            max=1440,
            error="duration_minutes must be between 1 and 1440",
        ),
    )
    notes = fields.String(
        allow_none=True,
        load_default=None,
        validate=validate.Length(max=1000),
    )

    @validates("duration_minutes")
    def validate_duration_minutes(self, value, **kwargs):
        if value is None:
            raise ValidationError("duration_minutes is required")
        if value <= 0:
            raise ValidationError("duration_minutes must be greater than 0")
        if value > 1440:
            raise ValidationError("duration_minutes cannot exceed 1440 (24 hours)")

    @validates("notes")
    def validate_notes_length(self, value, **kwargs):
        if value is not None and len(value) > 1000:
            raise ValidationError("Notes cannot exceed 1000 characters")


class WorkoutExerciseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = WorkoutExercise
        load_instance = True
        sqla_session = db.session
        include_fk = True

    id = fields.Integer(dump_only=True)
    workout_id = fields.Integer(dump_only=True)
    exercise_id = fields.Integer(dump_only=True)
    reps = fields.Integer(
        required=True,
        validate=validate.Range(min=0, error="reps must be greater than or equal to 0"),
    )
    sets = fields.Integer(
        required=True,
        validate=validate.Range(min=0, error="sets must be greater than or equal to 0"),
    )
    duration_seconds = fields.Integer(
        required=True,
        validate=validate.Range(
            min=0,
            error="duration_seconds must be greater than or equal to 0",
        ),
    )

    @validates("reps")
    def validate_reps(self, value, **kwargs):
        if value is None:
            raise ValidationError("reps is required")
        if value < 0:
            raise ValidationError("reps must be greater than or equal to 0")

    @validates("sets")
    def validate_sets(self, value, **kwargs):
        if value is None:
            raise ValidationError("sets is required")
        if value < 0:
            raise ValidationError("sets must be greater than or equal to 0")

    @validates("duration_seconds")
    def validate_duration_seconds(self, value, **kwargs):
        if value is None:
            raise ValidationError("duration_seconds is required")
        if value < 0:
            raise ValidationError("duration_seconds must be greater than or equal to 0")

    @validates_schema
    def validate_has_activity(self, data, **kwargs):
        reps = data.get("reps", 0)
        sets = data.get("sets", 0)
        duration_seconds = data.get("duration_seconds", 0)
        if reps <= 0 and sets <= 0 and duration_seconds <= 0:
            raise ValidationError(
                "At least one of reps, sets, or duration_seconds must be greater than 0"
            )


exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
workout_exercise_schema = WorkoutExerciseSchema()
workout_exercises_schema = WorkoutExerciseSchema(many=True)
