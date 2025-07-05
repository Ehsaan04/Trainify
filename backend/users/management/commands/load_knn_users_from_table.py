from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import ClientProfile
from datetime import datetime
import pytz

User = get_user_model()

# Mapping from table terms to model choices
GOAL_MAP = {
    'Gain Muscle': 'gain_muscle',
    'Gain Weight': 'gain_muscle',  # you can adjust this if needed
    'Lose Weight': 'lose_weight',
    'Maintain Current Weight': 'maintain_weight'
}

ACTIVITY_MAP = {
    'Sedentary': 'sedentary',
    'Moderately Active': 'moderately_active',
    'Very Active': 'very_active'
}

GENDER_MAP = {
    'Male': 'male',
    'Female': 'female',
    'Other': 'other'
}

# Users from the table (DOB format = DD/MM/YYYY)
TEST_USERS = [
    ("EhsaanR",      "31/03/2004", 166, 62, "Male",   "Gain Muscle",              "Moderately Active"),
    ("EhsaanR1",     "17/05/2005", 152, 57, "Male",   "Gain Weight",              "Sedentary"),
    ("EhsaanR2",     "14/05/2005", 154, 60, "Male",   "Lose Weight",              "Moderately Active"),
    ("EhsaanR3",     "31/03/2004", 165, 62, "Male",   "Gain Muscle",              "Moderately Active"),
    ("EhsaanR4",     "12/12/2005", 160, 59, "Male",   "Maintain Current Weight",  "Sedentary"),
    ("EhsaanR5",     "24/06/2003", 149, 56, "Female", "Gain Muscle",              "Very Active"),
    ("ZinoRecords",  "10/05/2004", 165, 53, "Male",   "Gain Muscle",              "Moderately Active"),
]

class Command(BaseCommand):
    help = "Bulk create users from the KNN test table"

    def handle(self, *args, **kwargs):
        for username, dob_str, height, weight, gender, goal, activity in TEST_USERS:
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f"User {username} already exists. Skipping."))
                continue

            # Parse date of birth
            dob = datetime.strptime(dob_str, "%d/%m/%Y").date()

            user = User.objects.create_user(
                username=username,
                email=f"{username.lower()}@example.com",
                password="testpass123",
                first_name=username,
                last_name="Test",
                is_client=True
            )

            ClientProfile.objects.create(
                user=user,
                date_of_birth=dob,
                gender=GENDER_MAP[gender],
                height=height,
                weight=weight,
                goal=GOAL_MAP[goal],
                activity_level=ACTIVITY_MAP[activity],
                dietary_preference="any",  # default
            )

            self.stdout.write(self.style.SUCCESS(f"Created user: {username}"))

        self.stdout.write(self.style.SUCCESS("✅ All users created successfully."))
