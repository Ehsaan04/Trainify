from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from .forms import ClientSignupForm, TrainerSignupForm, CustomLoginForm
from .models import TrainerProfile, ClientProfile, PTRequest, CustomUser, WeightProgress, MealPlan, WorkoutPlan, WorkoutPlanDay, WorkoutPlanRating, Season, Leaderboard, MealPlanNote, WorkoutPlanNote, SavedWorkout
from django.views.decorators.csrf import csrf_exempt
import json
from .utils.workout_generator_new import generate_workout_plan, load_exercise_data
from .utils.meal_generator_new import generate_meal_new
from .utils.knn_recommender import get_top_recommended_workouts_for_client


# Create your views here.
def home_page(request):
    return render(request, 'home.html')

#Client signup view
def client_signup(request):
    if request.method == 'POST':
        form = ClientSignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            #Redirects to Vue frontend
            return redirect('http://localhost:5173/')
    else:
        form = ClientSignupForm()
    return render(request, 'users/registration/client_signup.html', {'form': form})

#Trainer signup view
def trainer_signup(request):
    if request.method == 'POST':
        form = TrainerSignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            #Redirects to Vue frontend
            return redirect('http://localhost:5173/')
    else:
        form = TrainerSignupForm()
    return render(request, 'users/registration/trainer_signup.html', {'form': form})

@csrf_exempt
def logout_view(request):
    logout(request) 
    return redirect('/') 

class CustomLoginView(LoginView):
    template_name = 'users/registration/login.html' 
    #Uses CustomLoginForm defined in forms.py 
    authentication_form = CustomLoginForm  

@login_required
def get_user_type(request):
    user = request.user
    if user.is_trainer:
        user_type = "Trainer"
    elif user.is_client:
        user_type = "Client"
    else:
        user_type = "Invalid"
    return JsonResponse({
        "user_type": user_type

    }
    )

#Fetches all the data for a user that logs in
def get_user_data(request):
    #Stores the currently logged in user
    user = request.user

    if user.is_trainer:
        #Stores trainer profile of currently logged in trainer
        trainer_profile = user.trainer_profile
        #Returns selected trainer data as JSON response
        return JsonResponse({
            "user_type": "Trainer",
            "first_name": user.first_name,
            "last_name": user.last_name,
            "bio": trainer_profile.bio,  
            "profile_picture_url": trainer_profile.profile_picture.url if trainer_profile.profile_picture else None,  
        })

    elif user.is_client:
        #Stores client profile of currently logged in client
        client_profile = user.client_profile 

        #Initialises data of client's trainer, in case there isn't one
        trainer_data = None

        if client_profile.trainer:
            #Filters TrainerProfile objects to find trainer assigned to the client if there is one
            trainer_profile = TrainerProfile.objects.filter(user=client_profile.trainer).first()
            #Returns data of the client's trainer
            trainer_data = {
                "id": client_profile.trainer.id,
                "username": client_profile.trainer.username,
                "first_name": client_profile.trainer.first_name,
                "last_name": client_profile.trainer.last_name,
                "email": client_profile.trainer.email,
                "bio": trainer_profile.bio if trainer_profile else None,
                "profile_picture_url": trainer_profile.profile_picture.url if trainer_profile and trainer_profile.profile_picture else None,
            }

        #Returns desired client data
        return JsonResponse({
            "user_type": "Client",
            "id": client_profile.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            #Returns date in desired format
            "date_of_birth": client_profile.date_of_birth.strftime('%Y-%m-%d'), 
            "height": client_profile.height,
            "weight": client_profile.weight,
            "goal": client_profile.get_goal_display(),
            "dietary_preference": client_profile.dietary_preference,
            "profile_picture_url": client_profile.profile_picture.url if client_profile.profile_picture else None,
            "has_trainer": client_profile.trainer is not None,  
            "trainer": trainer_data,  
        })

    else:
        return JsonResponse({"user_type": "Invalid"})


def search_trainers(request):
    #Retrieves query parameter from URL containing username
    query = request.GET.get('username', '').strip()

    #If there is a query, performs search 
    #Trainer profile has foreign key "user"
    #user__username refers to use on the related user objective
    #icontains does a case insensitive search using Django's ORM
    trainers = TrainerProfile.objects.filter(user__username__icontains=query) if query else []
    data = [
        {
            'username': trainer.user.username,
            'bio': trainer.bio,
        }
        for trainer in trainers
    ]
    return JsonResponse({'trainers': data})

@csrf_exempt
def send_request(request):
    if request.method == 'POST':
        #Gets client profile of currently logged in user and parses JSON body that came with POST request
        client = request.user.client_profile
        data = json.loads(request.body)

        #Gets trainer username from received JSON payload
        trainer_username = data.get('trainer_username')

        #Finds the CustomUser with matching trainer username
        trainer_user = get_object_or_404(CustomUser, username=trainer_username, is_trainer=True)

        #Using the found CustomUser, gets the corresponding TrainerProfile
        trainer = get_object_or_404(TrainerProfile, user=trainer_user)

        #If the request is a duplicate (same client and trainer) stops it going through
        if PTRequest.objects.filter(client=client, trainer=trainer, status='pending').exists():
            return JsonResponse({'error': 'You already have a pending request to this trainer.'}, status=400)

        #Creates new request
        PTRequest.objects.create(client=client, trainer=trainer)
        return JsonResponse({'success': 'Request sent successfully.'})

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def view_requests(request):
    #Gets trainer profile of currently logged in trainer
    trainer = request.user.trainer_profile

    #Filters all requests to get pending requests assigned to that trainer
    requests = PTRequest.objects.filter(trainer=trainer, status='pending')

    #Loops through all requests and returns them as JSON
    data = [
        {
            'id': r.id,
            'client_username': r.client.user.username,
            'message': r.message,
            'created_at': r.created_at,
        }
        for r in requests
    ]
    return JsonResponse({'requests': data})

@csrf_exempt
def respond_to_request(request, request_id):
    trainer = request.user.trainer_profile
    pt_request = get_object_or_404(PTRequest, id=request_id, trainer=trainer)

    #Reads JSON body and extracts value from action key
    data = json.loads(request.body) 
    action = data.get("action") 

    if action == 'approve':
        #Sets status to approved and saves this change to database
        pt_request.status = 'approved'
        pt_request.save()

        #Sets the logged in trainer as the trainer of the client who sent the request
        pt_request.client.trainer = trainer.user
        pt_request.client.save()
        return JsonResponse({'success': 'Request approved.'})
    
    elif action == 'reject':
        #Sets status to rejected and saves this change to the database
        pt_request.status = 'rejected'
        pt_request.save()
        return JsonResponse({'success': 'Request rejected.'})
    
    #If this block is reached, an invalid action was received
    else:
        return JsonResponse({'error': f'Received action didnt match an expected value {action}'}, status=400)

@login_required
def get_trainer_clients(request):
    if not hasattr(request.user, 'trainer_profile'):
        return JsonResponse({'error': 'You must be a trainer to view clients.'}, status=403)

    #Fetches all clients assigned to the logged in trainer
    clients = ClientProfile.objects.filter(trainer=request.user)

    #Loops through each client and returns the necessary data
    client_data = [
        {
            'id': client.id,
            'username': client.user.username,
            'first_name': client.user.first_name,
            'last_name': client.user.last_name,
            'email': client.user.email,
            'date_of_birth': client.date_of_birth.strftime('%Y-%m-%d'),
            'gender': client.gender,
            'height': client.height,
            'weight': client.weight,
            'goal': client.goal,
            'goal_label': client.get_goal_display(),

            "priority_muscles": client.priority_muscles,
            'profile_picture': client.profile_picture.url if client.profile_picture else None,

            'protein_multiplier': client.protein_multiplier if client.protein_multiplier else 1.8,
            'daily_calories': client.daily_calories if client.daily_calories else 0,
            'daily_carbs': client.daily_carbs if client.daily_carbs else 0,
            'daily_protein': client.daily_protein if client.daily_protein else 0,
            'daily_fat': client.daily_fat if client.daily_fat else 0,
            'daily_fiber': client.daily_fiber if client.daily_fiber else 0,
        }
        for client in clients
    ]

    return JsonResponse({'clients': client_data}, safe=False)

@csrf_exempt 
def update_weight(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = request.user 

            if not hasattr(request.user, 'client_profile'):
                return JsonResponse({"error": "User is not a client."}, status=403)

            client_profile = user.client_profile

            #Extracts data from JSON 
            weight = data.get("weight")
            date_str = data.get("date")
            is_current = data.get("is_current", False)

            if not weight or not date_str:
                return JsonResponse({"error": "Weight and date are required."}, status=400)

            #Converts date string to a Django DateField compatible format
            weight_date = parse_date(date_str)
            if not weight_date:
                return JsonResponse({"error": "Invalid date format."}, status=400)

            #Store weight in WeightProgress
            WeightProgress.objects.create(client=client_profile, date=weight_date, weight=weight)

            #If weight entry was marked as current weight updates ClientProfile
            if is_current:
                client_profile.weight = weight
                client_profile.save()

            return JsonResponse({"message": "Weight updated successfully."}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)


@login_required
def get_weight_progress(request):
    try:
        user = request.user
        
        #Ensure user has a client profile
        if not hasattr(user, 'client_profile'):
            return JsonResponse({"error": "User is not a client."}, status=403)

        client_profile = user.client_profile

        #Retrieves all weight progress entries for the client
        weight_data = WeightProgress.objects.filter(client=client_profile).order_by('date')

        #Formats data for response
        data = [
            {"date": weight.date.strftime("%Y-%m-%d"), "weight": weight.weight}
            for weight in weight_data
        ]

        return JsonResponse({"weight_progress": data}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
def get_client_weight_progress(request, client_id):
    try:
        user = request.user

        if not user.is_trainer:
            return JsonResponse({"error": "Only trainers can access this endpoint."}, status=403)

        client = get_object_or_404(ClientProfile, id=client_id)

        # Ensure the client belongs to this trainer
        if client.trainer != user:
            return JsonResponse({"error": "Unauthorized access to this client's data."}, status=403)

        weight_data = WeightProgress.objects.filter(client=client).order_by('date')
        data = [
            {"date": entry.date.strftime("%Y-%m-%d"), "weight": entry.weight}
            for entry in weight_data
        ]
        return JsonResponse({"weight_progress": data}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
@csrf_exempt
def generate_meal_plan(request, client_id):
    try:
        client = ClientProfile.objects.get(id=client_id)
        data = json.loads(request.body)
        num_meals = data.get('num_meals', 3)

        #Clears old meals
        MealPlan.objects.filter(client=client).delete()

        #Keeps track of foods that have been used already
        previous_foods = set()

        meal_plans = []

        for meal_number in range(1, num_meals + 1):
            #Uses generate_meal_new function imported from script in utils folder
            #Uses PuLP to generate meal plan fitting client's targets
            meal_data = generate_meal_new(client, meal_number, previous_foods, num_meals)

            #Iterates through each food returned by the function
            for item in meal_data:
                #Saves meal to database
                meal = MealPlan.objects.create(
                    client=client,
                    meal_number=meal_number,
                    food_name=item['food_name'],
                    weight_in_grams=item['weight_in_grams'],
                    calories=item['calories'],
                    protein=item['protein'],
                    carbs=item['carbs'],
                    fats=item['fats'],
                    fiber=item.get('fiber', 0),
                    servings=item.get('servings', 1)
            
                )

                #Constructs JSON friendly response to get sent back to frontend to be displayed
                meal_plans.append({
                    'meal_number': meal_number,
                    'food_name': item['food_name'],
                    'weight_in_grams': item['weight_in_grams'],
                    'calories': item['calories'],
                    'protein': item['protein'],
                    'carbs': item['carbs'],
                    'fats': item['fats'],
                    'fiber': item.get('fiber', 0),
                    'servings': item.get('servings', 1)
                })

        return JsonResponse({'meal_plans': meal_plans}, status=200)

    except ClientProfile.DoesNotExist:
        return JsonResponse({'error': 'Client not found.'}, status=404)
    
@csrf_exempt
def regenerate_single_meal(request, client_id, meal_number):
    if request.method == "POST":
        try:
            client = ClientProfile.objects.get(id=client_id)

            #Gets foods in the current meal plan, excluding the current meal that is being re-generated
            #These foods are excluded from the re-generation process
            previous_foods = set(
                MealPlan.objects.filter(client=client).exclude(meal_number=meal_number).values_list("food_name", flat=True)
            )

            #Deletes the meal plan that is being replaced
            MealPlan.objects.filter(client=client, meal_number=meal_number).delete()

            data = json.loads(request.body)
            num_meals = data.get("num_meals", 3)

            meal_data = generate_meal_new(client, meal_number, previous_foods, num_meals)
            saved_meals = []

            #Stores new meal in the database
            for item in meal_data:
                MealPlan.objects.create(
                    client=client,
                    meal_number=meal_number,
                    food_name=item['food_name'],
                    weight_in_grams=item['weight_in_grams'],
                    calories=item['calories'],
                    protein=item['protein'],
                    carbs=item['carbs'],
                    fats=item['fats'],
                    fiber=item.get('fiber', 0),
                    servings=item.get('servings', 1),
                )
                saved_meals.append(item)

            return JsonResponse({'meal_number': meal_number, 'foods': saved_meals}, status=200)

        except ClientProfile.DoesNotExist:
            return JsonResponse({'error': 'Client not found.'}, status=404)



def get_saved_meal_plan(request, client_id):
    try:
        #Gets the ClientProfile assigned to client_id
        client = ClientProfile.objects.get(id=client_id)

        #Gets the meal plans assigned to this client
        meals = MealPlan.objects.filter(client=client).order_by("meal_number", "food_name")

        if meals.exists():
            latest_created_at = meals.first().created_at.strftime('%Y-%m-%d %H:%M:%S')
        else:
            latest_created_at = None

        #Loops through the meals and returns all meals as JSON
        meal_data = [
            {
                "meal_number": meal.meal_number,
                "food_name": meal.food_name,
                "weight_in_grams": meal.weight_in_grams,
                "calories": meal.calories,
                "protein": meal.protein,
                "carbs": meal.carbs,
                "fats": meal.fats,
                "fiber": meal.fiber,
                "servings": meal.servings
            }
            for meal in meals
        ]

        return JsonResponse({"meal_plans": meal_data,
                             "generated_at": latest_created_at}, status=200)

    except ClientProfile.DoesNotExist:
        return JsonResponse({"error": "Client not found"}, status=404)
    

@login_required
@csrf_exempt
def save_meal_plan_note(request, client_id):
    if request.method == "POST":
        try:
            client = ClientProfile.objects.get(id=client_id)

            #Gets value of note text from request body
            note_text = json.loads(request.body).get("note", "")

            #Stores note in database
            MealPlanNote.objects.update_or_create(client=client, defaults={"note": note_text})
            return JsonResponse({"message": "Note saved."})
        except ClientProfile.DoesNotExist:
            return JsonResponse({"error": "Client not found"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

@login_required
def get_meal_plan_note(request, client_id):
    note = MealPlanNote.objects.filter(client_id=client_id).values_list('note', flat=True).first()
    return JsonResponse({"note": note or ""})

@login_required
def get_workout_plan_note(request, client_id):
    if request.method == "GET":
        note = WorkoutPlanNote.objects.filter(client_id=client_id).values_list('note', flat=True).first()
        return JsonResponse({"note": note or ""})


@login_required
@csrf_exempt
def save_workout_plan_note(request, client_id):
    if request.method == "POST":
        try:
            #Gets client object by id
            client = ClientProfile.objects.get(id=client_id)

            #Gets note content from json payload
            note_text = json.loads(request.body).get("note", "")

            #Creates WorkoutPlanNote object or updates existing one
            WorkoutPlanNote.objects.update_or_create(client=client, defaults={"note": note_text})
            return JsonResponse({"message": "Note saved."})
        
        except ClientProfile.DoesNotExist:
            return JsonResponse({"error": "Client not found"}, status=404)
        
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

@csrf_exempt
def generate_workout_plan_view(request, client_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            #Gets number of days for program from request body
            workout_days = data.get("workout_days", 3)

            #Gets the muscle groups to train for each day
            muscle_groups_per_day = data.get("muscle_groups_per_day", [])

            #Gets difficuty if provided, otherwise defaults to intermediate
            difficulty_level = data.get("difficulty_level", "Intermediate")

            #Gets available equipment provided
            equipment_available = data.get("equipment_available", ["Dumbbell", "Barbell"])

            #Gets client's priority muscles
            priority_muscles = data.get("priority_muscles", [])

            client = ClientProfile.objects.get(id=client_id)

            #Deletes previous workout plan
            WorkoutPlan.objects.filter(client=client).delete()

            #Generates the plan using external script in utils folder
            generated_plan = generate_workout_plan(
                workout_days, muscle_groups_per_day, difficulty_level, equipment_available, priority_muscles=priority_muscles
            )

            #Saves the plan to the database
            new_plan = WorkoutPlan.objects.create(
                client=client,
                training_frequency=len(generated_plan)
            )

            #Saves each day of plan to database
            for day_number, exercises in generated_plan.items():
                WorkoutPlanDay.objects.create(
                    workout_plan=new_plan,
                    day_number=int(day_number.replace("Day ", "")),
                    exercises=exercises
                )

            #Returns generated plan as JSON for frontend
            return JsonResponse({
                "message": "Workout plan generated and saved!",
                "workout_plan": generated_plan,
                "plan_id": new_plan.id
            }, status=201)

        except ClientProfile.DoesNotExist:
            return JsonResponse({"error": "Client not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=405)

@csrf_exempt
def refresh_exercise(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            #Gets target muscle, mechanics, and equipment from selected exercise to refresh
            target_muscle = data.get("target_muscle", "").strip().lower()
            mechanics = data.get("mechanics", "").strip().lower()
            allowed_equipment = [eq.strip().lower() for eq in data.get("allowed_equipment", [])]

            #Loads exercise dataset
            df = load_exercise_data()

            #Filters/narrows down the dataframe, only keeping the rows that match the conditions specified
            df = df[df["Exercise Classification"].str.strip().str.lower() == "bodybuilding"]
            df = df[df["Target Muscle Group"].str.lower().str.contains(target_muscle)]
            df = df[df["Mechanics"].str.lower() == mechanics]
            df = df[df["Primary Equipment"].str.lower().isin(allowed_equipment)]  

            if not df.empty:
                #sample(1) chooses a random row from the filtered df
                #iloc[0] accesses first row from sampled df 
                new_exercise = df.sample(1).iloc[0]
                return JsonResponse({
                    "new_exercise": {
                        "exercise_name": new_exercise["Exercise"],
                        "target_muscle": new_exercise["Target Muscle Group"],
                        "equipment": new_exercise["Primary Equipment"],
                        "mechanics": new_exercise["Mechanics"]
                    }
                })
            else:
                return JsonResponse({"new_exercise": None})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)



@csrf_exempt
def save_workout_plan(request, client_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            #Gets workout plan from request body
            workout_plan = data.get("workout_plan", {})

            client = ClientProfile.objects.get(id=client_id)

            #Gets the most recent workout plan, in the event that multiple are saved
            workout_plan_obj = WorkoutPlan.objects.filter(client=client).last()

            if not workout_plan_obj:
                return JsonResponse({"error": "No workout plan found to update."}, status=404)

            #Update WorkoutPlanDays with the new exercises, deletes old WorkoutPlanDay first
            WorkoutPlanDay.objects.filter(workout_plan=workout_plan_obj).delete()

            #Stores new workout plan in database
            for day_number, exercises in workout_plan.items():
                WorkoutPlanDay.objects.create(
                    workout_plan=workout_plan_obj,
                    day_number=int(day_number.replace("Day ", "")),
                    exercises=exercises
                )

            return JsonResponse({"message": "Workout plan saved successfully!"}, status=200)

        except ClientProfile.DoesNotExist:
            return JsonResponse({"error": "Client not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=405)




def get_saved_workout_plan(request, client_id):
    try:
        client = ClientProfile.objects.get(id=client_id)
        latest_plan = WorkoutPlan.objects.filter(client=client).order_by("-created_at").first()

        if not latest_plan:
            return JsonResponse({"workout_plan": None}, status=200)

        #Fetch all workout days for the latest plan
        workout_days = WorkoutPlanDay.objects.filter(workout_plan=latest_plan).order_by("day_number")
        formatted_plan = {
            f"Day {day.day_number}": day.exercises for day in workout_days
        }

        return JsonResponse({"workout_plan": formatted_plan,
                             "plan_id": latest_plan.id}, status=200)

    except ClientProfile.DoesNotExist:
        return JsonResponse({"error": "Client not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

@csrf_exempt
@login_required
def rate_workout_plan(request):
    if request.method == "POST":
        try:
            user = request.user
            if not hasattr(user, 'client_profile'):
                return JsonResponse({"error": "User is not a client."}, status=403)

            client = user.client_profile

            #Get plan id, rating, and name from json payload
            data = json.loads(request.body)
            plan_id = data.get("plan_id")
            rating = data.get("rating")
            workout_name = data.get("workout_name", "")

            #If any required values or missing don't let the rating go through
            if not plan_id or not rating:
                return JsonResponse({"error": "Missing plan_id or rating."}, status=400)

            workout_plan = get_object_or_404(WorkoutPlan, id=plan_id)

            rating_obj, created = WorkoutPlanRating.objects.update_or_create(
                client=client,
                workout_plan=workout_plan,
                defaults={"rating": rating, "workout_name": workout_name}
            )

            return JsonResponse({"message": "Rating and name submitted."}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)

@login_required
def get_workout_plan_rating(request, plan_id):
    try:
        #Gets client profile if logged in client
        client = request.user.client_profile

        #Filters their ratings and gets the first one (rating for their current plan)
        rating_object = WorkoutPlanRating.objects.filter(client=client, workout_plan_id=plan_id).first()

        #if it's a valid object, returns the rating as JSON
        if rating_object:
            return JsonResponse({"rating": rating_object.rating}, status=200)
        
        else:

            return JsonResponse({"rating": None}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def get_recommended_workouts(request):
    try:
        client = request.user.client_profile

        #Makes use of KNN recommender, which returns top rated workouts from similar clients
        recommended_plans = get_top_recommended_workouts_for_client(client)

        data = []
        #Loops through recommended plans and adds them to data, which is returned to frontend
        for plan in recommended_plans:
            top_rating = plan.ratings.order_by('-rating').first()
            rating = plan.ratings.filter(client=client).first()
            data.append({
                "plan_id": plan.id,
                "training_frequency": plan.training_frequency,
                "created_at": plan.created_at.strftime('%Y-%m-%d'),
                "workout_name": top_rating.workout_name if top_rating else "Unnamed Plan",
                "rated_by": top_rating.client.user.username if top_rating else "Unknown"
            })

        return JsonResponse({"recommendations": data}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
#Allows a specific workout plan to be fetched by its ID
def get_workout_plan_by_id(request, plan_id):
    try:
        plan = WorkoutPlan.objects.get(id=plan_id)
        days = WorkoutPlanDay.objects.filter(workout_plan=plan).order_by("day_number")

        formatted = {
            f"Day {day.day_number}": day.exercises for day in days
        }

        return JsonResponse({"workout_plan": formatted}, status=200)
    except WorkoutPlan.DoesNotExist:
        return JsonResponse({"error": "Plan not found."}, status=404)
    

@csrf_exempt
def create_season(request):
    if request.method == "POST":
        if not request.user.is_trainer:
            return JsonResponse({"error": "Only trainers can create seasons."}, status=403)
        
        #Gets data from create season form from frontend
        data = json.loads(request.body)
        name = data.get("name")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        first_place_reward = data.get("first_place_reward")
        second_place_reward = data.get("second_place_reward")
        third_place_reward = data.get("third_place_reward")

        trainer = request.user.trainer_profile

        #Creates the season object based on the logged in trainer and the received data
        season = Season.objects.create(
            trainer=trainer,
            name=name,
            start_date=start_date,
            end_date=end_date,
            first_place_reward=first_place_reward,
            second_place_reward=second_place_reward,
            third_place_reward=third_place_reward
        )

        return JsonResponse({"message": "Season created.", "season_id": season.id})
    return JsonResponse({"error": "Invalid request method."}, status=405)

@csrf_exempt
def assign_points(request):
    if request.method == "POST":
        if not request.user.is_trainer:
            return JsonResponse({"error": "Only trainers can assign points."}, status=403)
        
        #JSON payload consists of the ID of the client to assign points to, and number of points to assign
        data = json.loads(request.body)
        client_id = data.get("client_id")
        points = data.get("points")

        #Gets the client, object, and season
        client = get_object_or_404(ClientProfile, id=client_id)
        trainer = request.user.trainer_profile
        season = Season.objects.filter(trainer=trainer, is_active=True).first()

        if not season:
            return JsonResponse({"error": "No active season found."}, status=400)
        
        #Uses objects retrieved from db to create or get current leaderboard entry
        leaderboard_entry, created = Leaderboard.objects.get_or_create(
            client=client, trainer=trainer, season=season,
            defaults={"points": 0}
        )
        #Adds on assigned points and saves the objet
        leaderboard_entry.points += int(points)
        leaderboard_entry.save()

        return JsonResponse({"message": "Points assigned successfully.", "total_points": leaderboard_entry.points})
    return JsonResponse({"error": "Invalid request method."}, status=405)

@login_required
def get_leaderboard(request):
    user = request.user

    #Checks if logged in user is trainer
    if user.is_trainer:
        trainer = user.trainer_profile
    elif user.is_client:
        #If logged in user is  a client, checks if they have an assigned trainer
        if not user.client_profile.trainer:
            return JsonResponse({"error": "You have no trainer assigned."}, status=400)
        trainer = user.client_profile.trainer.trainer_profile
    else:
        return JsonResponse({"error": "Invalid user type."}, status=400)
    
    #Gets the season object
    season = Season.objects.filter(trainer=trainer, is_active=True).first()

    if not season:
        return JsonResponse({"error": "No active season."}, status=404)

    #Retrieves all leaderboard (entry) objects for the season
    entries = Leaderboard.objects.filter(trainer=trainer, season=season).order_by('-points')

    #Fetches username + points, for each user to show leaderboard on frontend
    data = [
        {
            "client_username": entry.client.user.username,
            "points": entry.points
        } for entry in entries
    ]

    rewards = {
        "first": season.first_place_reward,
        "second": season.second_place_reward,
        "third": season.third_place_reward
    }

    return JsonResponse({"leaderboard": data, "season": season.name, "rewards": rewards, "end_date": season.end_date.isoformat()})



@login_required
def get_client_points(request, client_id):
    if not request.user.is_trainer:
        return JsonResponse({"error": "Unauthorized"}, status=403)
    
    #Gets trainer object and the corresponding season object
    trainer = request.user.trainer_profile
    season = Season.objects.filter(trainer=trainer, is_active=True).first()

    if not season:
        return JsonResponse({"error": "No active season"}, status=404)

    try:
        #Gets leaderboard entry for the desired client so their points can be accessed
        entry = Leaderboard.objects.get(client_id=client_id, trainer=trainer, season=season)
        return JsonResponse({"points": entry.points})
    except Leaderboard.DoesNotExist:
        return JsonResponse({"points": 0})  

@csrf_exempt
@login_required
def update_protein_multiplier(request, client_id):
    if request.method == "POST":
        try:
            client = ClientProfile.objects.get(id=client_id)
            data = json.loads(request.body)
            multiplier = float(data.get("protein_multiplier", 1.8))
            if 1.3 <= multiplier <= 2.5:
                client.protein_multiplier = multiplier
                client.save()
                return JsonResponse({"message": "Protein multiplier updated successfully."})
            else:
                return JsonResponse({"error": "Multiplier must be between 1.3 and 2.5"}, status=400)
        except ClientProfile.DoesNotExist:
            return JsonResponse({"error": "Client not found"}, status=404)
    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def update_client_goal(request, client_id):
    if request.method == "POST":
        try:
            client = ClientProfile.objects.get(id=client_id)
            data = json.loads(request.body)
            new_goal = data.get("goal")

            valid_goals = [choice[0] for choice in ClientProfile.WEIGHT_GOALS]
            if new_goal not in valid_goals:
                return JsonResponse({"error": "Invalid goal"}, status=400)

            client.goal = new_goal
            client.save()  
            return JsonResponse({
                "success": True,
                "goal": client.goal,
                "daily_calories": client.daily_calories,
                "daily_protein": client.daily_protein,
                "daily_carbs": client.daily_carbs,
                "daily_fat": client.daily_fat,
                "daily_fiber": client.daily_fiber
            })
        except ClientProfile.DoesNotExist:
            return JsonResponse({"error": "Client not found"}, status=404)

@csrf_exempt
@login_required
def unlink_client(request, client_id):
    if request.method == "POST":
        try:
            client = ClientProfile.objects.get(id=client_id)

            if client.trainer != request.user:
                return JsonResponse({'error': 'You do not have permission to unlink this client.'}, status=403)

            client.trainer = None
            client.save()
            return JsonResponse({'message': 'Client unlinked successfully.'})
        except ClientProfile.DoesNotExist:
            return JsonResponse({'error': 'Client not found.'}, status=404)

@csrf_exempt
@login_required
def save_recommended_workout(request, plan_id):
    try:
        client = request.user.client_profile
        workout_plan = get_object_or_404(WorkoutPlan, id=plan_id)

        #Creates SavedWorout object, or ignores if already saved
        SavedWorkout.objects.get_or_create(client=client, workout_plan=workout_plan)

        return JsonResponse({"message": "Workout plan saved successfully."}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def get_saved_recommended_workouts(request):
    try:
        client = request.user.client_profile
        saved = SavedWorkout.objects.filter(client=client).select_related('workout_plan')
        data = []

        #iterates through client's saved workouts and returns to frontend 
        for item in saved:
            plan = item.workout_plan
            top_rating = plan.ratings.order_by('-rating').first()
            days = WorkoutPlanDay.objects.filter(workout_plan=plan).order_by("day_number")
            exercises = {
                f"Day {day.day_number}": day.exercises for day in days
            }

            data.append({
                "plan_id": plan.id,
                "training_frequency": plan.training_frequency,
                "created_at": plan.created_at.strftime('%Y-%m-%d'),
                "workout_name": top_rating.workout_name if top_rating else "Unnamed Plan",
                "rated_by": top_rating.client.user.username if top_rating else "Unknown",
                "workout_plan": exercises
            })

        return JsonResponse({"saved_workouts": data}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
@csrf_exempt
@login_required
def remove_saved_workout(request, plan_id):
    if request.method != "DELETE":
        return JsonResponse({"error": "Invalid request method."}, status=405)
    
    try:
        client = request.user.client_profile
        #.delete() returns a tuple, first value consists of how many objects were deleted
        #breakdown of deleted objects is second value, only need to access firs to check if delete was successful
        result = SavedWorkout.objects.filter(client=client, workout_plan_id=plan_id).delete()
        deleted = result[0]

        if deleted:
            return JsonResponse({"message": "Workout removed from shortlist."}, status=200)
        else:
            return JsonResponse({"error": "Workout not found in shortlist."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def get_client_saved_workouts(request, client_id):
    try:
        #If the logged in user isn't a trainer, they aren't authorised to view the client's shortlist
        if not request.user.is_trainer:
            return JsonResponse({"error": "Unauthorized"}, status=403)
        
        #Gets the corresponding ClientProfile object based on ID, and then their saved workouts based on that
        client = get_object_or_404(ClientProfile, id=client_id)
        saved = SavedWorkout.objects.filter(client=client).select_related('workout_plan')

        #Stores the saved workouts and iterates through them
        data = []
        for item in saved:
            plan = item.workout_plan
            top_rating = plan.ratings.order_by('-rating').first()
            days = WorkoutPlanDay.objects.filter(workout_plan=plan).order_by("day_number")
            exercises = {
                f"Day {day.day_number}": day.exercises for day in days
            }

            #Serialises the plan data to be returned to the frontend
            data.append({
                "plan_id": plan.id,
                "training_frequency": plan.training_frequency,
                "created_at": plan.created_at.strftime('%Y-%m-%d'),
                "workout_name": top_rating.workout_name if top_rating else "Unnamed Plan",
                "rated_by": top_rating.client.user.username if top_rating else "Unknown",
                "workout_plan": exercises
            })

        return JsonResponse({"saved_workouts": data}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@login_required
def assign_saved_workout(request, client_id, plan_id):
    try:
        client = get_object_or_404(ClientProfile, id=client_id)
        source_plan = get_object_or_404(WorkoutPlan, id=plan_id)

        #Creates a copy of the desired workout plan to assign
        new_plan = WorkoutPlan.objects.create(
            client=client,
            training_frequency=source_plan.training_frequency
        )

        #Copies all workout plan days and assigns them to the workout plan
        source_days = WorkoutPlanDay.objects.filter(workout_plan=source_plan)
        for day in source_days:
            WorkoutPlanDay.objects.create(
                workout_plan=new_plan,
                day_number=day.day_number,
                exercises=day.exercises
            )

        return JsonResponse({"message": "Workout plan set as active."}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
