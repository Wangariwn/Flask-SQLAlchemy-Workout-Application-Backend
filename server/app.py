from flask import Flask, make_response
from flask_migrate import Migrate

from models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

migrate = Migrate(app, db)

db.init_app(app)


# Define Routes here


# ---------- Workouts ----------


@app.route("/workouts", methods=["GET"])
def get_workouts():
    """List all workouts"""
    return make_response({"message": "List all workouts"}, 200)


@app.route("/workouts/<int:id>", methods=["GET"])
def get_workout(id):
    """Show a single workout with its associated exercises
    Stretch goal: include reps/sets/duration data from WorkoutExercises
    """
    return make_response(
        {"message": f"Show workout {id} with associated exercises"},
        200,
    )


@app.route("/workouts", methods=["POST"])
def create_workout():
    """Create a workout"""
    return make_response({"message": "Create a workout"}, 201)


@app.route("/workouts/<int:id>", methods=["DELETE"])
def delete_workout(id):
    """Delete a workout
    Stretch goal: delete associated WorkoutExercises
    """
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
