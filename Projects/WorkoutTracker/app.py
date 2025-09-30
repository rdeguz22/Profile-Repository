import sys
import os
sys.path.append(os.path.abspath('.'))

from models.user import User
from models.workout import Workout
from models.exercise import Exercise
from models.set import Set
from models.goal import Goal

def main():
    while True:
        print("\n=== Workout Tracker ===")
        print("1. Add User")
        print("2. List Users")
        print("3. Get User by ID")
        print("4. Add Workout")
        print("5. List Workouts by User")
        print("6. Get Workout by ID")
        print("7. Add Exercise")
        print("8. List Exercises by Workout")
        print("9. Get Exercise by ID")
        print("10. Add Set")
        print("11. List Sets by Exercise")
        print("12. Get Set by ID")
        print("13. Add Goal")
        print("14. List Goals by User")
        print("15. Get Goal by ID")
        print("0. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            username = input("Enter username: ")
            email = input("Enter email: ")
            User.add_user(username, email)

        elif choice == "2":
            for u in User.list_users():
                print(u)

        elif choice == "3":
            user_id = int(input("User ID: "))
            user = User.get_user(user_id)
            print(user if user else "User not found.")

        elif choice == "4":
            user_id = int(input("User ID: "))
            workout_date = input("Workout Date (YYYY-MM-DD): ")
            workout_type = input("Workout Type: ")
            notes = input("Notes (optional): ")
            Workout.add_workout(user_id, workout_date, workout_type, notes)

        elif choice == "5":
            user_id = int(input("User ID: "))
            for w in Workout.list_workouts(user_id):
                print(w)

        elif choice == "6":
            workout_id = int(input("Workout ID: "))
            workout = Workout.get_workout(workout_id)
            print(workout if workout else "Workout not found.")

        elif choice == "7":
            workout_id = int(input("Workout ID: "))
            exercise_name = input("Exercise Name: ")
            muscle_group = input("Muscle Group (optional): ")
            Exercise.add_exercise(workout_id, exercise_name, muscle_group)

        elif choice == "8":
            workout_id = int(input("Workout ID: "))
            for e in Exercise.list_exercises(workout_id):
                print(e)

        elif choice == "9":
            exercise_id = int(input("Exercise ID: "))
            exercise = Exercise.get_exercise(exercise_id)
            print(exercise if exercise else "Exercise not found.")

        elif choice == "10":
            exercise_id = int(input("Exercise ID: "))
            reps = int(input("Reps: "))
            weight = float(input("Weight (optional, press Enter for 0): "))
            Set.add_set(exercise_id, reps, weight if weight > 0 else None)

        elif choice == "11":
            exercise_id = int(input("Exercise ID: "))
            for s in Set.list_sets(exercise_id):
                print(s)

        elif choice == "12":
            set_id = int(input("Set ID: "))
            workout_set = Set.get_set(set_id)
            print(workout_set if workout_set else "Set not found.")

        elif choice == "13":
            user_id = int(input("User ID: "))
            exercise_name = input("Exercise Name: ")
            target_weight = float(input("Target Weight: "))
            target_reps = int(input("Target Reps: "))
            Goal.add_goal(user_id, exercise_name, target_weight, target_reps)

        elif choice == "14":
            user_id = int(input("User ID: "))
            for g in Goal.list_goals(user_id):
                print(g)

        elif choice == "15":
            goal_id = int(input("Goal ID: "))
            goal = Goal.get_goal(goal_id)
            print(goal if goal else "Goal not found.")

        elif choice == "0":
            print("Goodbye.")
            break

        else:
            print("Invalid choice. Try again.")