from flask import Flask, make_response, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import *
from schemas import (
    exercise_schema,
    exercises_schema,
    workout_schema,
    workouts_schema,
    workout_exercise_schema,
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


def error_response(message, status=400):
    if isinstance(message, str):
        message = [message]
    return make_response({"errors": message}, status)


# Define Routes here


# ---------- Workouts ----------


@app.route("/workouts", methods=["GET"])
def get_workouts():
    """List all workouts"""
    workouts = Workout.query.all()
    return make_response(workouts_schema.dump(workouts), 200)


@app.route("/workouts/<int:id>", methods=["GET"])
def get_workout(id):
    """Show a single workout with its associated exercises
    Stretch goal: include reps/sets/duration data from WorkoutExercises
    """
    workout = db.session.get(Workout, id)
    if not workout:
        return error_response("Workout not found", 404)

    data = workout_schema.dump(workout)
    data["exercises"] = [
        {
            **exercise_schema.dump(we.exercise),
            "reps": we.reps,
            "sets": we.sets,
            "duration_seconds": we.duration_seconds,
            "workout_exercise_id": we.id,
        }
        for we in workout.workout_exercises
    ]
    return make_response(data, 200)


@app.route("/workouts", methods=["POST"])
def create_workout():
    """Create a workout"""
    json_data = request.get_json()
    if not json_data:
        return error_response("Request body must be JSON")

    try:
        workout = workout_schema.load(json_data)
        db.session.add(workout)
        db.session.commit()
        return make_response(workout_schema.dump(workout), 201)
    except ValidationError as err:
        return error_response(err.messages)
    except ValueError as err:
        db.session.rollback()
        return error_response(str(err))
    except IntegrityError:
        db.session.rollback()
        return error_response("Could not create workout due to a database constraint")


@app.route("/workouts/<int:id>", methods=["DELETE"])
def delete_workout(id):
    """Delete a workout
    Stretch goal: delete associated WorkoutExercises
    """
    workout = db.session.get(Workout, id)
    if not workout:
        return error_response("Workout not found", 404)

    db.session.delete(workout)
    db.session.commit()
    return make_response("", 204)


# ---------- Exercises ----------


@app.route("/exercises", methods=["GET"])
def get_exercises():
    """List all exercises"""
    return make_response({"message": "List all exercises"}, 200)


@app.route("/exercises/<int:id>", methods=["GET"])
def get_exercise(id):
    """Show an exercise and associated workouts"""
    return make_response(
        {"message": f"Show exercise {id} with associated workouts"},
        200,
    )


@app.route("/exercises", methods=["POST"])
def create_exercise():
    """Create an exercise"""
    return make_response({"message": "Create an exercise"}, 201)


@app.route("/exercises/<int:id>", methods=["DELETE"])
def delete_exercise(id):
    """Delete an exercise
    Stretch goal: delete associated WorkoutExercises
    """
    return make_response("", 204)


# ---------- WorkoutExercises (join) ----------


@app.route(
    "/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises",
    methods=["POST"],
)
def add_exercise_to_workout(workout_id, exercise_id):
    """Add an exercise to a workout, including reps/sets/duration"""
    return make_response(
        {
            "message": (
                f"Add exercise {exercise_id} to workout {workout_id} "
                "with reps/sets/duration"
            )
        },
        201,
    )


if __name__ == "__main__":
    app.run(port=5555, debug=True)
