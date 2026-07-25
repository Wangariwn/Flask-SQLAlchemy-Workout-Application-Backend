from marshmallow import fields, validate, validates, ValidationError
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
        validate=validate.Length(min=1, max=100),
    )
    category = fields.String(
        required=True,
        validate=validate.OneOf(VALID_CATEGORIES),
    )
    equipment_needed = fields.Boolean(required=True)

    @validates("name")
    def validate_name_not_blank(self, value, **kwargs):
        if not value or not value.strip():
            raise ValidationError("Name cannot be blank")


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
    notes = fields.String(allow_none=True, load_default=None)

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
        validate=validate.Range(min=0),
    )
    sets = fields.Integer(
        required=True,
        validate=validate.Range(min=0),
    )
    duration_seconds = fields.Integer(
        required=True,
        validate=validate.Range(min=0),
    )

    @validates("reps")
    def validate_reps_required(self, value, **kwargs):
        if value is None:
            raise ValidationError("reps is required")

    @validates("sets")
    def validate_sets_required(self, value, **kwargs):
        if value is None:
            raise ValidationError("sets is required")

    @validates("duration_seconds")
    def validate_duration_required(self, value, **kwargs):
        if value is None:
            raise ValidationError("duration_seconds is required")


exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
workout_exercise_schema = WorkoutExerciseSchema()
workout_exercises_schema = WorkoutExerciseSchema(many=True)
