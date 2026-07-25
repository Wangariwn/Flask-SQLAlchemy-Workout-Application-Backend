from flask import Flask, make_response, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import (
    db,
    Exercise,
    Workout,
    WorkoutExercise,
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
    return make_response({"errors": [message] if isinstance(message, str) else message}, status)


# ---------- Workout Routes ----------


@app.get("/workouts")
def get_workouts():
    workouts = Workout.query.all()
    return make_response(workouts_schema.dump(workouts), 200)


@app.get("/workouts/<int:id>")
def get_workout(id):
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


@app.post("/workouts")
def create_workout():
    json_data = request.get_json()
    if not json_data:
        return error_response("Request body must be JSON")

    try:
        data = workout_schema.load(json_data)
        workout = Workout(
            date=data["date"],
            duration_minutes=data["duration_minutes"],
            notes=data.get("notes"),
        )
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


@app.delete("/workouts/<int:id>")
def delete_workout(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return error_response("Workout not found", 404)

    db.session.delete(workout)
    db.session.commit()
    return make_response({}, 204)


# ---------- Exercise Routes ----------


@app.get("/exercises")
def get_exercises():
    exercises = Exercise.query.all()
    return make_response(exercises_schema.dump(exercises), 200)


@app.get("/exercises/<int:id>")
def get_exercise(id):
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return error_response("Exercise not found", 404)

    data = exercise_schema.dump(exercise)
    data["workouts"] = [
        {
            **workout_schema.dump(we.workout),
            "reps": we.reps,
            "sets": we.sets,
            "duration_seconds": we.duration_seconds,
            "workout_exercise_id": we.id,
        }
        for we in exercise.workout_exercises
    ]
    return make_response(data, 200)


@app.post("/exercises")
def create_exercise():
    json_data = request.get_json()
    if not json_data:
        return error_response("Request body must be JSON")

    try:
        data = exercise_schema.load(json_data)
        exercise = Exercise(
            name=data["name"],
            category=data["category"],
            equipment_needed=data["equipment_needed"],
        )
        db.session.add(exercise)
        db.session.commit()
        return make_response(exercise_schema.dump(exercise), 201)
    except ValidationError as err:
        return error_response(err.messages)
    except ValueError as err:
        db.session.rollback()
        return error_response(str(err))
    except IntegrityError:
        db.session.rollback()
        return error_response("Exercise name must be unique")


@app.delete("/exercises/<int:id>")
def delete_exercise(id):
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return error_response("Exercise not found", 404)

    db.session.delete(exercise)
    db.session.commit()
    return make_response({}, 204)


# ---------- Join: Add Exercise to Workout ----------


@app.post("/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises")
def add_exercise_to_workout(workout_id, exercise_id):
    workout = db.session.get(Workout, workout_id)
    if not workout:
        return error_response("Workout not found", 404)

    exercise = db.session.get(Exercise, exercise_id)
    if not exercise:
        return error_response("Exercise not found", 404)

    json_data = request.get_json()
    if not json_data:
        return error_response("Request body must be JSON")

    try:
        data = workout_exercise_schema.load(json_data)
        workout_exercise = WorkoutExercise(
            workout_id=workout_id,
            exercise_id=exercise_id,
            reps=data["reps"],
            sets=data["sets"],
            duration_seconds=data["duration_seconds"],
        )
        db.session.add(workout_exercise)
        db.session.commit()
        return make_response(workout_exercise_schema.dump(workout_exercise), 201)
    except ValidationError as err:
        return error_response(err.messages)
    except ValueError as err:
        db.session.rollback()
        return error_response(str(err))
    except IntegrityError:
        db.session.rollback()
        return error_response(
            "This exercise is already added to the workout, or a constraint failed"
        )


@app.get("/")
def index():
    return make_response(
        {
            "message": "Workout Tracker API",
            "endpoints": [
                "GET /workouts",
                "GET /workouts/<id>",
                "POST /workouts",
                "DELETE /workouts/<id>",
                "GET /exercises",
                "GET /exercises/<id>",
                "POST /exercises",
                "DELETE /exercises/<id>",
                "POST /workouts/<workout_id>/exercises/<exercise_id>/workout_exercises",
            ],
        },
        200,
    )


if __name__ == "__main__":
    app.run(port=5555, debug=True)
