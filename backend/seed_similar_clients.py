from users.models import CustomUser, ClientProfile
from django.utils.timezone import datetime

trainer = CustomUser.objects.create_user(
    username="trainerdemo",
    email="trainer.demo@example.com",
    password="testpass123",
    first_name="Trainer",
    last_name="Demo",
    is_trainer=True
)

print("Trainer account created: trainerdemo / testpass123")

clients = [
    {
        "first_name": "Carlos",
        "last_name": "Mendes",
        "username": "carlosm",
        "email": "carlos.m@example.com",
        "dob": "1995-09-12",
        "gender": "Male",
        "height": 178,
        "weight": 88,
        "goal": "lose_weight",
        "priority_muscles": ["chest", "back", "shoulders"],
        "activity_level": "lightly_active",
    },
    {
        "first_name": "Aiden",
        "last_name": "Clarke",
        "username": "aidenc",
        "email": "aiden.c@example.com",
        "dob": "1997-04-05",
        "gender": "Male",
        "height": 182,
        "weight": 95,
        "goal": "lose_weight",
        "priority_muscles": ["chest", "shoulders", "triceps"],
        "activity_level": "moderately_active",
    },
    {
        "first_name": "Marcus",
        "last_name": "Evans",
        "username": "marcuse",
        "email": "marcus.ev@example.com",
        "dob": "1996-01-25",
        "gender": "Male",
        "height": 177,
        "weight": 91,
        "goal": "lose_weight",
        "priority_muscles": ["back", "core", "biceps"],
        "activity_level": "lightly_active",
    },
    {
        "first_name": "Julian",
        "last_name": "Scott",
        "username": "julians",
        "email": "julian.s@example.com",
        "dob": "1994-11-03",
        "gender": "Male",
        "height": 180,
        "weight": 90,
        "goal": "lose_weight",
        "priority_muscles": ["chest", "back", "hamstrings"],
        "activity_level": "lightly_active",
    },
    {
        "first_name": "Nathan",
        "last_name": "Brooks",
        "username": "nathanb",
        "email": "nathan.b@example.com",
        "dob": "1998-06-17",
        "gender": "Male",
        "height": 183,
        "weight": 93,
        "goal": "lose_weight",
        "priority_muscles": ["shoulders", "core", "quadriceps"],
        "activity_level": "moderately_active",
    },
]

for client in clients:
    user = CustomUser.objects.create_user(
        username=client["username"],
        email=client["email"],
        password="testpass123",
        first_name=client["first_name"],
        last_name=client["last_name"],
        is_client=True,
    )

    ClientProfile.objects.create(
        user=user,
        date_of_birth=datetime.strptime(client["dob"], "%Y-%m-%d").date(),
        gender=client["gender"],
        height=client["height"],
        weight=client["weight"],
        goal=client["goal"],
        priority_muscles=client["priority_muscles"],
        activity_level=client["activity_level"],
        trainer=None 
    )

print("5 similar clients created successfully.")
