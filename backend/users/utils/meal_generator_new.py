from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpInteger, LpStatus
import numpy as np
import pandas as pd
import os

#Load CSV containing food data per serving
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, "food_data_with_fiber.csv")

try:
    food_data = pd.read_csv(file_path)
except FileNotFoundError:
    raise FileNotFoundError(f"File could not be found at '{file_path}'")

def generate_meal_new(client, meal_number, previous_foods, num_meals=3):
    #Daily macronutrient targets are split across meals
    target_calories = client.daily_calories / num_meals
    target_protein = client.daily_protein / num_meals
    target_carbs = client.daily_carbs / num_meals
    target_fat = client.daily_fat / num_meals
    target_fiber = client.daily_fiber / num_meals if client.daily_fiber else 8  

    #Define 10% tolerance level for targets
    tolerance = 0.1

    #Filters out previous foods
    available_foods = food_data[~food_data["Food Name"].isin(previous_foods)].copy()

    #If available foods after filtering is too short uses full list
    if len(available_foods) < 3:
        available_foods = food_data.copy()

    #Extract values
    food_names = available_foods["Food Name"].tolist()
    calories = available_foods["Calories per Serving"].tolist()
    protein = available_foods["Protein per Serving"].tolist()
    carbs = available_foods["Carbs per Serving"].tolist()
    fats = available_foods["Fat per Serving"].tolist()
    fiber = available_foods["Fiber per Serving"].tolist()

    #Stores number of foods
    n = len(food_names)

    #Setting up LP problem as integer minimisation problem
    prob = LpProblem("Meal_Plan", LpMinimize)
    x = [LpVariable(f"x_{i}", lowBound=0, cat=LpInteger) for i in range(n)]

    #Randomized objective to encourage variety
    np.random.seed()

    #Weights are randomly distributed from 1 to 1.3, n weights are made for each food
    #These weights are used as the costs in the objective function
    weights = np.random.uniform(1.0, 1.3, n)

    #Defines the objective function, minimise the weighted sum of servings
    prob += lpSum([weights[i] * x[i] for i in range(n)]), "Randomised Total Cost"

    #Macronutrient constraints with tolerance
    #Calorie constraints
    prob += lpSum([calories[i] * x[i] for i in range(n)]) >= (1 - tolerance) * target_calories
    prob += lpSum([calories[i] * x[i] for i in range(n)]) <= (1 + tolerance) * target_calories

    #Protein constraints
    prob += lpSum([protein[i] * x[i] for i in range(n)]) >= (1 - tolerance) * target_protein
    prob += lpSum([protein[i] * x[i] for i in range(n)]) <= (1 + tolerance) * target_protein

    #Carbohydrate constraints
    prob += lpSum([carbs[i] * x[i] for i in range(n)]) >= (1 - tolerance) * target_carbs
    prob += lpSum([carbs[i] * x[i] for i in range(n)]) <= (1 + tolerance) * target_carbs

    #Fat constraints
    prob += lpSum([fats[i] * x[i] for i in range(n)]) >= (1 - tolerance) * target_fat
    prob += lpSum([fats[i] * x[i] for i in range(n)]) <= (1 + tolerance) * target_fat

    #Fiber constraints
    prob += lpSum([fiber[i] * x[i] for i in range(n)]) >= (1 - tolerance) * target_fiber
    prob += lpSum([fiber[i] * x[i] for i in range(n)]) <= (1 + tolerance) * target_fiber

    #Solve the defined problem
    result_status = prob.solve()

    #Process result and return structured food plan
    meal_plan = []
    if LpStatus[prob.status] == "Optimal":
        for i in range(n):
            #Extracts decision variable after problem has been solved
            #This contains the number of servings for that food
            servings = x[i].varValue

            #Any food with more than 0 servings is appended to the meal plan
            if servings and servings > 0:
                meal_plan.append({
                    'food_name': food_names[i],
                    'weight_in_grams': servings * available_foods.iloc[i]["Serving Weight (g)"], 
                    'calories': round(calories[i] * servings, 2),
                    'protein': round(protein[i] * servings, 2),
                    'carbs': round(carbs[i] * servings, 2),
                    'fats': round(fats[i] * servings, 2),
                    'fiber': round(fiber[i] * servings, 2),
                    'servings': float(servings)

                })
                previous_foods.add(food_names[i])
    else:
        print("Failed to find an optimal solution")

    return meal_plan
