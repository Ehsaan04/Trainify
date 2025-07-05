from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from datetime import date
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.

#Custom User model for authentication
class CustomUser(AbstractUser):
    is_trainer = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)

    def __str__(self):
        return self.username

#Trainer profile
class TrainerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='trainer_profile')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/trainers/', blank=True, null=True)

    def __str__(self):
        return self.user.username

#Client profile
class ClientProfile(models.Model):
    WEIGHT_GOALS = [
        ('lose_weight', 'Lose Weight'),
        ('gain_muscle', 'Gain Weight'),
        ('maintain_weight', 'Maintain Current Weight'),
    ]
    DIETARY_PREFERENCES = [
        ('any', 'No Preference'),
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('pescatarian', 'Pescatarian'),
        ('ketogenic', 'Ketogenic'),
        ('paleo', 'Paleo'),
        ('gluten_free', 'Gluten-Free'),
        ('dairy_free', 'Dairy-Free'),
        ('low_carb', 'Low-Carb'),
    ]

    ACTIVITY_LEVELS = [
        ('sedentary', 'Sedentary (Little to no exercise)'),
        ('lightly_active', 'Lightly Active (Light exercise 1-3 days per week)'),
        ('moderately_active', 'Moderately Active (Moderate exercise 3-5 days per week)'),
        ('very_active', 'Very Active (Hard exercise 6-7 days per week)'),
        ('super_active', 'Super Active (Very intense exercise daily)'),
    ]

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    PRIORITY_MUSCLES_CHOICES = [
        ('chest', 'Chest'),
        ('back', 'Back'),
        ('biceps', 'Biceps'),
        ('triceps', 'Triceps'),
        ('shoulders', 'Shoulders'),
        ('quadriceps', 'Quadriceps'),
        ('hamstrings', 'Hamstrings'),
        ('glutes', 'Glutes'),
        ('forearms', 'Forearms')
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='client_profile')
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='other')
    height = models.FloatField()  #Height in cm
    weight = models.FloatField()  #Weight in kg
    trainer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='clients')
    profile_picture = models.ImageField(upload_to='profile_pictures/clients/', blank=True, null=True)
    goal = models.CharField(max_length=20, choices=WEIGHT_GOALS, default='maintain_weight')
    priority_muscles = models.JSONField(default=list, blank=True)
    dietary_preference = models.CharField(max_length=20, choices=DIETARY_PREFERENCES, default='any')
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_LEVELS, default='moderately_active')

    protein_multiplier = models.FloatField(
        default=1.8,
        validators=[MinValueValidator(1.3), MaxValueValidator(2.5)],
        help_text="Grams of protein per kg of bodyweight (1.3 - 2.5)"
    )
    daily_calories = models.IntegerField(null=True, blank=True)
    daily_carbs = models.FloatField(null=True, blank=True)  # grams
    daily_protein = models.FloatField(null=True, blank=True)  # grams
    daily_fat = models.FloatField(null=True, blank=True)  # grams
    daily_fiber = models.FloatField(null=True, blank=True)  # grams
    macronutrient_last_updated = models.DateTimeField(null=True, blank=True)

    @property
    def age(self):
        today = date.today()
        if self.date_of_birth:
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
                #If birthday hasn't occurred subtracts 1, otherwise subtracts 0
            )
        return None
    
    def __str__(self):
        return self.user.username

    
    def clean(self):
        if self.date_of_birth and self.date_of_birth > date.today():
            raise ValidationError("Date of birth cannot be in the future.")
        
    
    def calculate_macronutrients(self):
        #Basal Metabolic Rate (BMR) calculation using Mifflin-St Jeor Equation
        if self.gender == "male":
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        else:
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age - 161

        #Activity multipliers based on activity level
        activity_multipliers = {
            'sedentary': 1.2,
            'lightly_active': 1.375,
            'moderately_active': 1.55,
            'very_active': 1.725,
            'super_active': 1.9,
        }
        activity_multiplier = activity_multipliers.get(self.activity_level, 1.55)

        #Calculates maintenance calories based on activity multiplier
        maintenance_calories = bmr * activity_multiplier

        #Adjust calories based on goal
        if self.goal == "lose_weight":
            #500 calorie deficit for weight loss
            daily_calories = maintenance_calories - 500  
        elif self.goal == "gain_muscle":
            #500 calorie surplus for muscle/weight gain
            daily_calories = maintenance_calories + 500  
        else:
            #No adjustment for maintaining weight
            daily_calories = maintenance_calories  

        #Daily macronutrient targets
        #Uses custom protein multiplier
        daily_protein = self.weight * self.protein_multiplier

        #25% of calories from fat (9 kcal per gram)
        daily_fat = daily_calories * 0.25 / 9  

        #Remaining calories for carbs
        daily_carbs = (daily_calories - (daily_protein * 4 + daily_fat * 9)) / 4  

        #14g per 1000 kcal
        daily_fiber = daily_calories * 14 / 1000  

        #Returns macros to 2 decimal places
        return {
            "daily_calories": round(daily_calories),
            "daily_carbs": round(daily_carbs, 2),
            "daily_protein": round(daily_protein, 2),
            "daily_fat": round(daily_fat, 2),
            "daily_fiber": round(daily_fiber, 2),
        }
    
    def save(self, *args, **kwargs):
        #Macros are updated before model is saved to ensure up to date targets
        macros = self.calculate_macronutrients()
        self.daily_calories = macros["daily_calories"]
        self.daily_carbs = macros["daily_carbs"]
        self.daily_protein = macros["daily_protein"]
        self.daily_fat = macros["daily_fat"]
        self.daily_fiber = macros["daily_fiber"]
        self.macronutrient_last_updated = now()

        #Calls original save method
        super().save(*args, **kwargs)  

class WorkoutPlan(models.Model):
    client = models.ForeignKey("ClientProfile", on_delete=models.CASCADE, related_name="workout_plans")
    training_frequency = models.PositiveIntegerField(help_text="Number of workout days per week")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Workout Plan for {self.client.user.username} - {self.created_at.strftime('%Y-%m-%d')}"

class WorkoutPlanDay(models.Model):
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name="days")
    day_number = models.PositiveIntegerField(help_text="Day number in the workout plan (e.g., Day 1, Day 2)")
    exercises = models.JSONField(help_text="List of exercises for the day")

    def __str__(self):
        return f"{self.workout_plan.client.user.username} - Day {self.day_number}"

class MealPlan(models.Model):
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name="meal_plans")
    created_at = models.DateTimeField(auto_now_add=True)
    meal_number = models.IntegerField()  
    food_name = models.CharField(max_length=255)
    weight_in_grams = models.FloatField()
    calories = models.FloatField()
    protein = models.FloatField()
    carbs = models.FloatField()
    fats = models.FloatField()
    fiber = models.FloatField(default=0.0)
    servings = models.FloatField(default=1.0)


    def __str__(self):
        return f"Meal {self.meal_number} for {self.client.user.username}"

    
class MealPlanNote(models.Model):
    client = models.OneToOneField(ClientProfile, on_delete=models.CASCADE, related_name='meal_plan_note')
    note = models.TextField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

class WorkoutPlanNote(models.Model):
    client = models.OneToOneField(ClientProfile, on_delete=models.CASCADE, related_name='workout_plan_note')
    note = models.TextField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Workout Note for {self.client.user.username}"


class Appointment(models.Model):
    trainer = models.ForeignKey(
        'TrainerProfile', on_delete=models.CASCADE, related_name='appointments_as_trainer'
    )
    client = models.ForeignKey(
        'ClientProfile', on_delete=models.CASCADE, related_name='appointments'
    )
    title = models.CharField(max_length=255, help_text="Title of the appointment")
    description = models.TextField(blank=True, null=True, help_text="Optional description")
    start = models.DateTimeField(help_text="Start date and time of the appointment")
    end = models.DateTimeField(help_text="End date and time of the appointment")

    def __str__(self):
        return f"Appointment: {self.title} ({self.start} - {self.end})"

#Trainer Client Request
class PTRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='requests_sent')
    trainer = models.ForeignKey(TrainerProfile, on_delete=models.CASCADE, related_name='requests_received')
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request from {self.client.user.username} to {self.trainer.user.username} - {self.status}"


class Leaderboard(models.Model):
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='leaderboard_entries')
    trainer = models.ForeignKey(TrainerProfile, on_delete=models.CASCADE, related_name='leaderboard')
    season = models.ForeignKey('Season', on_delete=models.CASCADE, related_name='leaderboard_entries', null=True, blank=True)
    points = models.PositiveIntegerField(default=0, help_text="Total points for the client")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('client', 'trainer', 'season')

    def __str__(self):
        return f"{self.client.user.username} - {self.points} points (Trainer: {self.trainer.user.username})"

class Season(models.Model):
    trainer = models.ForeignKey(TrainerProfile, on_delete=models.CASCADE, related_name='seasons')
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    first_place_reward = models.CharField(max_length=255)
    second_place_reward = models.CharField(max_length=255)
    third_place_reward = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.trainer.user.username})"

class WeightProgress(models.Model):
    client = models.ForeignKey(
        'ClientProfile', on_delete=models.CASCADE, related_name='weight_progress'
    )
    date = models.DateField(default=now, help_text="Date of recorded weight")
    weight = models.FloatField(help_text="Weight in kg")

    def __str__(self):
        return f"{self.client.user.username} - {self.weight} kg on {self.date}"
    
class WorkoutPlanRating(models.Model):
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='workout_ratings')
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)], help_text="Rating from 1 to 5")
    workout_name = models.CharField(max_length=255, help_text="Custom name for the workout", default="")

    def __str__(self):
        return f"{self.client.user.username} rated {self.workout_plan.id} as {self.rating}"

class SavedWorkout(models.Model):
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name="saved_workouts")
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('client', 'workout_plan')  

    def __str__(self):
        return f"{self.client.user.username} saved Plan {self.workout_plan.id}"
