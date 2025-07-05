import pandas as pd
import random
import os
from collections import defaultdict

def load_exercise_data():
    #Get CSV path
    base_path = os.path.dirname(__file__)
    csv_file = os.path.join(base_path, "exercise_database_full.csv")

    # Load CSV remove any potential trailing spaces
    df = pd.read_csv(csv_file)
    df.columns = [col.strip() for col in df.columns]

    #required columns
    must_have_columns = [
        "Exercise",
        "Difficulty Level",
        "Target Muscle Group",
        "Primary Equipment",
        "Exercise Classification",
        "Mechanics"
    ]
    missing = [col for col in must_have_columns if col not in df.columns]

    if missing:
        #If CSV has wrong structure, raise error
        raise ValueError(f"Missing columns in the CSV: {missing}. Found: {list(df.columns)}")

    return df

#Function that constructs the workout plan
def generate_workout_plan(workout_days, muscle_groups_per_day, difficulty_level, equipment_available, priority_muscles=None):
    df = load_exercise_data()

    df["Exercise Classification"] = df["Exercise Classification"].str.lower().str.strip()
    df = df[df["Exercise Classification"] == "bodybuilding"]

    if equipment_available:
        #Filters by provided available equipment
        df = df[df["Primary Equipment"].isin(equipment_available)]

    #Groups exercises by muscle group
    grouped_by_muscle = defaultdict(list)
    for _, entry in df.iterrows():
        muscle_list = [m.strip().lower() for m in str(entry["Target Muscle Group"]).split(",")]
        for m in muscle_list:
            grouped_by_muscle[m].append(entry)

    #Final workout plan structure
    final_plan = {}
    priority_muscles = [m.lower() for m in priority_muscles] if priority_muscles else []
    bigger_muscles = {"chest", "back", "quadriceps"} 

    for i, muscle_day in enumerate(muscle_groups_per_day, start=1):
        #Hard codes number of exercises per muscle depending on number of muscles chosen on a day
        muscle_count = len(muscle_day)
        if muscle_count == 1:
            per_muscle = 4
        elif muscle_count == 2:
            per_muscle = 3
        elif muscle_count == 3:
            per_muscle = 2
        else:
            per_muscle = 1  

        # Split by priority type
        day_priority = []
        day_big = []
        day_misc = []

        for raw_muscle in muscle_day:
            muscle = raw_muscle.strip().lower()
            if muscle not in grouped_by_muscle:
                continue 

            options = grouped_by_muscle[muscle]
            random.shuffle(options)  

            #Separate into compound and isolation exercises
            compounds = [ex for ex in options if str(ex.get("Mechanics", "")).strip().lower() == "compound"]
            isolations = [ex for ex in options if str(ex.get("Mechanics", "")).strip().lower() == "isolation"]

            selected = []

            #Always try to start with a compound movement
            if compounds:
                selected.append(random.choice(compounds))

            #Fill the rest with isolation, fall back if necessary
            needed_more = per_muscle - len(selected)
            already_picked = set(ex["Exercise"] for ex in selected)

            iso_pool = [ex for ex in isolations if ex["Exercise"] not in already_picked]
            other_pool = [ex for ex in options if ex["Exercise"] not in already_picked]

            if iso_pool:
                random.shuffle(iso_pool)
                selected.extend(iso_pool[:needed_more])

            if len(selected) < per_muscle:
                random.shuffle(other_pool)
                selected.extend(other_pool[:per_muscle - len(selected)])

            if muscle in priority_muscles:
                day_priority.extend(selected)
            elif muscle in bigger_muscles:
                day_big.extend(selected)
            else:
                day_misc.extend(selected)

        #Combines to get all exercises for a given day
        all_exercises = day_priority + day_big + day_misc

        final_plan[f"Day {i}"] = [
            {
                "exercise_name": ex["Exercise"],
                "target_muscle": ex["Target Muscle Group"],
                "equipment": ex["Primary Equipment"],
                "mechanics": ex["Mechanics"]
            } for ex in all_exercises
        ]

    return final_plan
