import random
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now, timedelta
from api.models import User, Auto, Parking, Place, Booking

User.objects.all().delete()
Auto.objects.all().delete()
Parking.objects.all().delete()
Place.objects.all().delete()
Booking.objects.all().delete()

parking_data = [
    ("Киевская", "Манаса", "Исанова", 8),
    ("Токтогула", "Исанова", "Тоголок-Молдо", 16),
    ("Киевская", "Абдрахманова", "Шопокова", 15),
    ("Чуй", "Абдрахманова", "Тыныстанова", 23),
    ("Московская", "Турусбекова", "Уметалиева", 10),
    ("Турусбекова", "Московская", "Боконбаева", 11),
]

parkings = []
for street, cross_at, cross_to, place_count in parking_data:
    parking = Parking.objects.create(
        street=street,
        cross_street_at=cross_at,
        cross_street_to=cross_to,
    )
    for i in range(1, place_count + 1):
        Place.objects.create(parking=parking, number=i, is_free=True)
    parkings.append(parking)

for i in range(1, 101):
    email = f"user{i}@example.com"
    user = User.objects.create(
        email=email,
        password=make_password("password123"),
        role=random.choice(["user", "admin"]),
    )

    auto_count = random.randint(1, 3)
    for j in range(auto_count):
        Auto.objects.create(
            user=user,
            plate=f"ABC{i}{j}",
            certificate=f"Cert{i}{j}",
            color=random.choice(["Red", "Blue", "Green", "Black", "White"]),
            brand=random.choice(["Toyota", "BMW", "Honda", "Ford", "Tesla"]),
        )

users = list(User.objects.all())
places = list(Place.objects.all())

for _ in range(70):
    user = random.choice(users)
    auto = random.choice(user.autos.all())
    place = random.choice(places)
    place.is_free = False
    place.save()
    start_time = now() + timedelta(days=random.randint(-10, 10))
    end_time = start_time + timedelta(hours=random.randint(1, 6))

    Booking.objects.create(
        place=place,
        auto=auto,
        datetime_at=start_time,
        datetime_to=end_time,
    )

print("Database populated successfully!")
