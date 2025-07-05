from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import ClientProfile, MealPlan, WorkoutPlan, WorkoutPlanDay, TrainerProfile, Season, Leaderboard, WeightProgress, WorkoutPlanRating
from .models import WorkoutPlan, WorkoutPlanRating
from datetime import date
import json

User = get_user_model()

#Tests for signup and login
class UserAuthTests(TestCase):
    def setUp(self):
        self.client = Client()

    #Signs up a client with dummy data in expected format
    def test_client_signup(self):
        response = self.client.post('/signup/client/', {
            'username': 'newclient',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'first_name': 'Client',
            'last_name': 'User',
            'email': 'client@example.com',
            'date_of_birth': '2000-01-01',
            'gender': 'Male',
            'height': 175,
            'weight': 70,
            'goal': 'gain_muscle',
            'priority_muscles': ['chest', 'back'],
            'activity_level': 'moderately_active',
        })

        #Checks for successful redirect
        self.assertEqual(response.status_code, 302)

        #Checks that database has successfully updated
        user = User.objects.get(username='newclient')

        #Checks that logged in user is now a client
        self.assertTrue(user.is_client)

        #Checks that signed up user also has a client profile
        self.assertTrue(ClientProfile.objects.filter(user=user).exists())

    #Signs up a trainer with dummy data in expected format
    def test_trainer_signup(self):
        response = self.client.post('/signup/trainer/', {
            'username': 'newtrainer',
            'password1': 'TrainerPass123!',
            'password2': 'TrainerPass123!',
            'first_name': 'Trainer',
            'last_name': 'User',
            'email': 'trainer@example.com',
            'bio': 'Experienced trainer in strength and conditioning.'
        })

        #Checks for successful redirect after signing up
        self.assertEqual(response.status_code, 302)

        #Checks that users db table has updated
        user = User.objects.get(username='newtrainer')

        #Checks that logged in user is trainer and has a trainer profile assigned to them
        self.assertTrue(user.is_trainer)
        self.assertTrue(TrainerProfile.objects.filter(user=user).exists())

    #Tests login with correct credentials
    def test_login_success(self):
        User.objects.create_user(username='loginuser', password='testpass', is_client=True)
        response = self.client.post('/login/', {
            'username': 'loginuser',
            'password': 'testpass'
        })

        #Checks successful redirect
        self.assertEqual(response.status_code, 302) 

    #Tests login with incorrect credentials
    def test_login_failure_wrong_password(self):
        User.objects.create_user(username='loginfail', password='correctpass')
        response = self.client.post('/login/', {
            'username': 'loginfail',
            'password': 'wrongpass'
        })

        #Checks that response is as expected (200 ok and expected message)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct username and password")

#Tests for checking meal plan generator
class MealPlanGenerationTests(TestCase):

    #Creates user so they can be authenticated and have a meal generated
    def setUp(self):
        self.user = User.objects.create_user(
            username='client1',
            password='testpass',
            is_client=True
        )

        #Assigns a client profile to the user with dummy data from which macros are calculated
        self.client_profile = ClientProfile.objects.create(
            user=self.user,
            date_of_birth=date(2000, 1, 1),
            gender='male',
            height=180,
            weight=75,
            goal='gain_muscle',
            activity_level='moderately_active',
        )
        self.client_profile.save()
        self.client = Client()
        self.client.force_login(self.user)

    
    def test_generate_meal_plan_endpoint(self):
        #Hits meal plan generator endpoint, creating a meal plan (number of meals set to 3)
        response = self.client.post(
            f'/generate-meal-plan/{self.client_profile.id}/',
            data={'num_meals': 3},
            content_type='application/json'
        )

        #Checks 200 ok response code 
        self.assertEqual(response.status_code, 200)

        #Checks that returned JSON has correct structure
        self.assertIn('meal_plans', response.json())
        self.assertGreater(len(response.json()['meal_plans']), 0)

        #Filters existing meal plans to only include ones assigned to test client
        meals = MealPlan.objects.filter(client=self.client_profile)
        self.assertTrue(meals.exists())

        #Sums up the total calories and macros for generated meal
        total_calories = sum(meal.calories for meal in meals)
        total_protein = sum(meal.protein for meal in meals)
        total_carbs = sum(meal.carbs for meal in meals)
        total_fats = sum(meal.fats for meal in meals)
        total_fiber = sum(meal.fiber for meal in meals)

        
        num_meals = 3
        tolerance = 0.10

        #Gets client's daily calorie and macro targets so they can be compared to meal
        target_calories = self.client_profile.daily_calories
        target_protein = self.client_profile.daily_protein
        target_carbs = self.client_profile.daily_carbs
        target_fats = self.client_profile.daily_fat
        target_fiber = self.client_profile.daily_fiber

        


        #Helper function to test if actual values are within specified tolerance level
        def assert_within_tolerance(total, target):
            lower = (1 - tolerance) * target
            upper = (1 + tolerance) * target
            self.assertGreaterEqual(total, lower)
            self.assertLessEqual(total, upper)

        #Assertions for actual meal plan totals and targets
        assert_within_tolerance(total_calories, target_calories)
        assert_within_tolerance(total_protein, target_protein)
        assert_within_tolerance(total_carbs, target_carbs)
        assert_within_tolerance(total_fats, target_fats)
        assert_within_tolerance(total_fiber, target_fiber)

#Tests for workout plan generation
class WorkoutPlanGenerationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='client2',
            password='testpass',
            is_client=True
        )

        #Creates client profile with dummy data
        self.client_profile = ClientProfile.objects.create(
            user=self.user,
            date_of_birth=date(2000, 1, 1),
            gender='male',
            height=175,
            weight=70,
            goal='maintain_weight',
            activity_level='lightly_active',
        )
        self.client_profile.save()
        self.client = Client()
        self.client.force_login(self.user)
    

    def test_generate_workout_plan(self):
        #Passes the required parameters in the expected format
        payload = {
            "workout_days": 3,
            "muscle_groups_per_day": [["chest", "triceps"], ["back", "biceps"], ["legs"]],
            "difficulty_level": "Intermediate",
            "equipment_available": ["Dumbbell", "Barbell"],
            "priority_muscles": ["chest", "biceps"]
        }

        #Hits the endpoint with a post request, passing the parameters and generating a workout plan
        response = self.client.post(
            f'/generate-workout-plan/{self.client_profile.id}/',
            data=json.dumps(payload),
            content_type='application/json'
        )

        #Assertions to check that generated plan has expected structure
        self.assertEqual(response.status_code, 201)
        self.assertIn("workout_plan", response.json())
        self.assertIn("plan_id", response.json())

        #Assertions to check that database entries are accurate
        plan_id = response.json()["plan_id"]
        plan = WorkoutPlan.objects.get(id=plan_id)
        self.assertEqual(plan.client, self.client_profile)

        days = WorkoutPlanDay.objects.filter(workout_plan=plan)
        self.assertEqual(days.count(), 3)

#Tests for gamification system
class GamificationTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        
        #Creates account for trainer and respective trainer profile
        self.trainer_user = self.User.objects.create_user(
            username='trainer1', password='trainerpass', is_trainer=True
        )
        self.trainer_profile = TrainerProfile.objects.create(user=self.trainer_user)


        #Creates account for client and respective client profile
        self.client_user = self.User.objects.create_user(
            username='client1', password='clientpass', is_client=True
        )
        self.client_profile = ClientProfile.objects.create(
            user=self.client_user,
            date_of_birth=date(2000, 1, 1),
            gender='male',
            height=175,
            weight=70,
            goal='maintain_weight',
            activity_level='lightly_active',
            trainer=self.trainer_user
        )

        #Trainer logs in
        self.client = Client()
        self.client.force_login(self.trainer_user)

        #Trainer creates a season 
        self.season = Season.objects.create(
            trainer=self.trainer_profile,
            name="Spring Challenge",
            start_date=date(2024, 3, 1),
            end_date=date(2024, 5, 1),
            first_place_reward="Free session",
            second_place_reward="Discounted merch",
            third_place_reward="Shoutout",
            is_active=True
        )

    #Test for assigning points to a client
    def test_assign_points_to_client(self):
        payload = {
            "client_id": self.client_profile.id,
            "points": 20
        }

        #Hits endpoint for assigning points
        response = self.client.post(
            "/assign-points/",
            data=json.dumps(payload),
            content_type="application/json"
        )

        #Checks that response is as expected
        self.assertEqual(response.status_code, 200)
        self.assertIn("total_points", response.json())
        self.assertEqual(response.json()["total_points"], 20)

        #Checks that the client's leaderboard entry has been updated
        entry = Leaderboard.objects.get(client=self.client_profile, season=self.season)
        self.assertEqual(entry.points, 20)

    def test_assign_points_without_active_season(self):
        #Deactivates season
        self.season.is_active = False
        self.season.save()

        payload = {
            "client_id": self.client_profile.id,
            "points": 15
        }

        #Hits endpoint for assigning points
        response = self.client.post(
            "/assign-points/",
            data=json.dumps(payload),
            content_type="application/json"
        )

        #Verifies that adding points was unsuccessful
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())
        self.assertEqual(response.json()["error"], "No active season found.")

class WeightUpdateTests(TestCase):
    #Creates user and client profile with dummy data
    def setUp(self):
        self.user = User.objects.create_user(
            username='client_weight',
            password='testpass',
            is_client=True
        )
        self.client_profile = ClientProfile.objects.create(
            user=self.user,
            date_of_birth=date(2000, 1, 1),
            gender='male',
            height=180,
            weight=75,
            goal='maintain_weight',
            activity_level='moderately_active',
        )
        self.client_profile.save()
        self.client = Client()
        self.client.force_login(self.user)

    def test_update_weight_progress_and_current_weight(self):
        payload = {
            "weight": 72.5,
            "date": "2024-04-01",
            "is_current": True
        }

        #Hits endpoint for updating weight
        response = self.client.post(
            "/api/updateWeight",
            data=json.dumps(payload),
            content_type="application/json"
        )

        #Verifies 200 ok response
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())

        #Checks database to see if weight entry was successfully added
        progress = WeightProgress.objects.filter(client=self.client_profile).first()
        self.assertIsNotNone(progress)
        self.assertEqual(progress.weight, 72.5)
        self.assertEqual(str(progress.date), "2024-04-01")

        #Checks that client's current weight has been updated
        self.client_profile.refresh_from_db()
        self.assertEqual(self.client_profile.weight, 72.5)




class KNNRecommenderTests(TestCase):
    def setUp(self):
        self.client = Client()

        #Creates client who will receive recommendations
        self.target_user = User.objects.create_user(
            username='target_user', password='pass', is_client=True
        )
        self.target_client = ClientProfile.objects.create(
            user=self.target_user,
            date_of_birth=date(1998, 1, 1),
            gender='male',
            height=175,
            weight=70,
            goal='gain_muscle',
            activity_level='moderately_active',
        )
        self.client.force_login(self.target_user)

        #Creates 5 similar clients to target client
        for i in range(1, 6):  
            user = User.objects.create_user(
                username=f'similar{i}', password='pass', is_client=True
            )
            profile = ClientProfile.objects.create(
                user=user,
                date_of_birth=date(1995 + i, 1, 1),
                gender='male',
                height=170 + i,
                weight=68 + i,
                goal='gain_muscle',
                activity_level='moderately_active',
            )
            plan = WorkoutPlan.objects.create(
                client=profile,
                #Frequencies either 3 or 4
                training_frequency=3 + (i % 2)  
            )
            WorkoutPlanRating.objects.create(
                client=profile,
                workout_plan=plan,
                #Ratings either 4 or 5 stars
                rating=4 + (i % 2),  
                workout_name=f"Plan {i}"
            )


        #Creates a client with very different attributes to target client
        self.different_user = User.objects.create_user(
            username='outlier', password='pass', is_client=True
        )
        self.different_client = ClientProfile.objects.create(
            user=self.different_user,
            date_of_birth=date(1960, 1, 1),
            gender='female',
            height=150,
            weight=50,
            goal='lose_weight',
            activity_level='sedentary',
        )
        self.outlier_plan = WorkoutPlan.objects.create(
            client=self.different_client,
            training_frequency=2
        )
        WorkoutPlanRating.objects.create(
            client=self.different_client,
            workout_plan=self.outlier_plan,
            rating=5,
            workout_name="Yoga for Seniors"
        )

    def test_knn_returns_recommendations(self):
            #Hits endpoint to get recommendations and verifies 200 ok response code 
            response = self.client.get('/get-recommended-workouts/')
            self.assertEqual(response.status_code, 200)

            #Checks that returned recommendations list has correct structure
            data = response.json()
            self.assertIn("recommendations", data)
            self.assertIsInstance(data["recommendations"], list)

            #Checks that recommendations are from the 5 similar clients
            #Also verifies that plan from outlier client is not included in recommendation
            recommended_names = [rec["workout_name"] for rec in data["recommendations"]]
            self.assertIn("Plan 1", recommended_names)
            self.assertIn("Plan 2", recommended_names)
            self.assertIn("Plan 3", recommended_names)
            self.assertIn("Plan 4", recommended_names)
            self.assertIn("Plan 5", recommended_names)
            self.assertNotIn("Yoga for Seniors", recommended_names)
