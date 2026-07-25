# Workout Tracker API

A Flask REST API for managing workouts and exercises. Workouts and exercises have a many-to-many relationship through a `WorkoutExercises` join table that stores reps, sets, and duration.

## Features

- Create, view, and delete workouts
- Create, view, and delete exercises
- Add an exercise to a workout (with reps, sets, and duration)
- Validations at the table, model, and schema levels
- Cascade deletes for associated `WorkoutExercises` records

## Models

| Model | Fields |
| --- | --- |
| **Exercise** | `id`, `name`, `category`, `equipment_needed` |
| **Workout** | `id`, `date`, `duration_minutes`, `notes` |
| **WorkoutExercise** | `id`, `workout_id`, `exercise_id`, `reps`, `sets`, `duration_seconds` |

### Relationships

- A `WorkoutExercise` belongs to a `Workout`
- A `WorkoutExercise` belongs to an `Exercise`
- A `Workout` has many `WorkoutExercises`
- An `Exercise` has many `WorkoutExercises`
- A `Workout` has many `Exercises` through `WorkoutExercises`
- An `Exercise` has many `Workouts` through `WorkoutExercises`

## Validations

### Table constraints
- Non-null columns for required fields
- Unique exercise names
- Check constraints (e.g. duration > 0, reps/sets/duration_seconds >= 0)
- Foreign keys with cascade delete
- Unique pair of `(workout_id, exercise_id)` on the join table

### Model validations (`@validates`)
- Exercise name must be non-empty
- Exercise category must be one of: Strength, Cardio, Flexibility, Balance
- Workout duration must be a positive integer
- WorkoutExercise reps, sets, and duration_seconds must be non-negative

### Schema validations (Marshmallow)
- Required fields enforced on create
- String length / OneOf / Range validators on request payloads

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/workouts` | List all workouts |
| `GET` | `/workouts/<id>` | Show a workout with exercises (includes reps/sets/duration) |
| `POST` | `/workouts` | Create a workout |
| `DELETE` | `/workouts/<id>` | Delete a workout (and associated WorkoutExercises) |
| `GET` | `/exercises` | List all exercises |
| `GET` | `/exercises/<id>` | Show an exercise with associated workouts |
| `POST` | `/exercises` | Create an exercise |
| `DELETE` | `/exercises/<id>` | Delete an exercise (and associated WorkoutExercises) |
| `POST` | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout |

## Installation

```bash
# Install dependencies
pipenv install

# Activate the virtual environment
pipenv shell

# From the server directory, apply migrations
cd server
export FLASK_APP=app.py
flask db upgrade

# (Only if migrations/ does not exist yet:)
# flask db init
# flask db migrate -m "create tables"
# flask db upgrade

# Seed sample data
python seed.py
```

## Run

```bash
cd server
export FLASK_APP=app.py

# Recommended
flask run --port=5555

# Or
python app.py
```

The API runs at [http://127.0.0.1:5555](http://127.0.0.1:5555).

## Example Requests

### Create an exercise
```bash
curl -X POST http://127.0.0.1:5555/exercises \
  -H "Content-Type: application/json" \
  -d '{"name": "Squat", "category": "Strength", "equipment_needed": false}'
```

### Create a workout
```bash
curl -X POST http://127.0.0.1:5555/workouts \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-07-25", "duration_minutes": 45, "notes": "Leg day"}'
```

### Add an exercise to a workout
```bash
curl -X POST http://127.0.0.1:5555/workouts/1/exercises/1/workout_exercises \
  -H "Content-Type: application/json" \
  -d '{"reps": 10, "sets": 3, "duration_seconds": 0}'
```

## Tech Stack

- Python 3.12
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Marshmallow / Marshmallow-SQLAlchemy
- SQLite
