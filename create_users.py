import django
import os

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sopdisplay_core.settings")  # Replace 'your_project' with your actual Django project name
django.setup()

from django.contrib.auth.models import User
from user_app.models import Profile

# Define a list of users with profile details
users_data = [
    {"id": 30, "username": "user101", "password": "pass101", "my_skill": 0, "matrix": "InterfaceAuto 101"},
    {"id": 31, "username": "user102", "password": "pass102", "my_skill": 1, "matrix": "InterfaceAuto 102"},
    {"id": 32, "username": "user103", "password": "pass103", "my_skill": 2, "matrix": "InterfaceAuto 103"},
    {"id": 33, "username": "user104", "password": "pass104", "my_skill": 1, "matrix": "InterfaceAuto 104"},
    {"id": 34, "username": "user105", "password": "pass105", "my_skill": 2, "matrix": "InterfaceAuto 105"},
]

# Create users and profiles
for user_info in users_data:
    user, created = User.objects.get_or_create(
        username=user_info["username"],
        defaults={"id": user_info["id"]}  # Set the given ID
    )
    if created:
        user.set_password(user_info["password"])
        user.save()
        
        # Create a corresponding profile with my_skill and matrix
        Profile.objects.create(
            user=user,
            my_skill=user_info["my_skill"],
            matrix=user_info["matrix"]
        )

        print(f"User {user.username} created successfully with ID {user.id}, my_skill: {user_info['my_skill']}, matrix: {user_info['matrix']}.")
    else:
        print(f"User {user.username} already exists.")

print("User creation process completed!")
