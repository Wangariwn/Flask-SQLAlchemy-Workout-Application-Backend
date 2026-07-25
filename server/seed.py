#!/usr/bin/env python3

from datetime import date

from app import app
from models import db, Exercise, Workout, WorkoutExercise

with app.app_context():
    # reset data and add new example data, committing to db
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()

    pushups = Exercise(
        name="Push-ups",
        category="Strength",
        equipment_needed=False,
    )
    running = Exercise(
        name="Running",
        category="Cardio",
        equipment_needed=False,
    )
    yoga = Exercise(
        name="Yoga Flow",
        category="Flexibility",
        equipment_needed=False,
    )
    deadlift = Exercise(
        name="Deadlift",
        category="Strength",
        equipment_needed=True,
    )
    planks = Exercise(
        name="Plank Hold",
        category="Balance",
        equipment_needed=False,
    )

    db.session.add_all([pushups, running, yoga, deadlift, planks])
    db.session.commit()

    workout_one = Workout(
        date=date(2026, 7, 20),
        duration_minutes=45,
        notes="Morning strength session",
    )
    workout_two = Workout(
        date=date(2026, 7, 22),
        duration_minutes=30,
        notes="Cardio and mobility",
    )
    workout_three = Workout(
        date=date(2026, 7, 25),
        duration_minutes=60,
        notes="Full body day",
    )

    db.session.add_all([workout_one, workout_two, workout_three])
    db.session.commit()

    links = [
        WorkoutExercise(
            workout_id=workout_one.id,
            exercise_id=pushups.id,
            reps=15,
            sets=3,
            duration_seconds=0,
        ),
        WorkoutExercise(
            workout_id=workout_one.id,
            exercise_id=deadlift.id,
            reps=8,
            sets=4,
            duration_seconds=0,
        ),
        WorkoutExercise(
            workout_id=workout_two.id,
            exercise_id=running.id,
            reps=0,
            sets=0,
            duration_seconds=1800,
        ),
        WorkoutExercise(
            workout_id=workout_two.id,
            exercise_id=yoga.id,
            reps=0,
            sets=0,
            duration_seconds=600,
        ),
        WorkoutExercise(
            workout_id=workout_three.id,
            exercise_id=planks.id,
            reps=0,
            sets=3,
            duration_seconds=60,
        ),
        WorkoutExercise(
            workout_id=workout_three.id,
            exercise_id=pushups.id,
            reps=20,
            sets=4,
            duration_seconds=0,
        ),
    ]

    db.session.add_all(links)
    db.session.commit()

    print("Seeded exercises, workouts, and workout_exercises successfully.")
