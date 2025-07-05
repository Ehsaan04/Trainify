from users.models import CustomUser, ClientProfile  
from django.utils.timezone import datetime

clients_data = [
    {
        "first_name": "Daniel",
        "last_name": "Reyes",
        "username": "danielr",
        "email": "daniel.reyes@example.com",
        "password": "testpass123",
        "dob": "1996-03-14",
        "gender": "Male",
        "height": 180,
        "weight": 92,
        "goal": "lose_weight",
        "priority_muscles": ["chest", "back", "shoulders"],
        "activity_level": "lightly_active",
    },
    {
        "first_name": "Priya",
        "last_name": "Nair",
        "username": "priyanair",
        "email": "priya.nair@example.com",
        "password": "testpass123",
        "dob": "1998-07-22",
        "gender": "Female",
        "height": 162,
        "weight": 58,
        "goal": "maintain_weight",
        "priority_muscles": ["glutes", "hamstrings", "shoulders"],
        "activity_level": "moderately_active",
    },
    {
        "first_name": "Elijah",
        "last_name": "Kim",
        "username": "elijahk",
        "email": "elijah.kim@example.com",
        "password": "testpass123",
        "dob": "2001-11-02",
        "gender": "Male",
        "height": 175,
        "weight": 68,
        "goal": "gain_muscle",
        "priority_muscles": ["biceps", "triceps", "chest"],
        "activity_level": "sedentary",
    },
    {
        "first_name": "Layla",
        "last_name": "Thompson",
        "username": "laylat",
        "email": "layla.thompson@example.com",
        "password": "testpass123",
        "dob": "1995-01-30",
        "gender": "Female",
        "height": 168,
        "weight": 70,
        "goal": "lose_weight",
        "priority_muscles": ["glutes", "hamstrings", "shoulders"],
        "activity_level": "very_active",
    },
    {
        "first_name": "Samir",
        "last_name": "Ali",
        "username": "samira",
        "email": "samir.ali@example.com",
        "password": "testpass123",
        "dob": "1990-05-09",
        "gender": "Male",
        "height": 185,
        "weight": 80,
        "goal": "maintain_weight",
        "priority_muscles": ["forearms", "back", "triceps"],
        "activity_level": "super_active",
    },
]

for client in clients_data:
    user = CustomUser.objects.create_user(
        username=client["username"],
        email=client["email"],
        password=client["password"],
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
    )

print("Dummy client accounts created successfully.")
