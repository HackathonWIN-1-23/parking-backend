from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    ROLE_CHOICES = (('admin', 'Admin'), ('user', 'User'))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email



class Auto(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='autos')
    plate = models.CharField(max_length=15, unique=True)
    certificate = models.CharField(max_length=255)
    color = models.CharField(max_length=50)
    brand = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.brand} ({self.plate})"


class Parking(models.Model):
    street = models.CharField(max_length=255)
    cross_street_at = models.CharField(max_length=255)
    cross_street_to = models.CharField(max_length=255)

    def __str__(self):
        return self.street


class Place(models.Model):
    STATUS_CHOICES = (('reserved', 'Reserved'), ('free', 'Free'), ('busy', 'Busy'))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='free')
    parking = models.ForeignKey(Parking, on_delete=models.CASCADE, related_name='places')

    def __str__(self):
        return f"Place {self.id} - {self.status}"


class Booking(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='bookings')
    auto = models.ForeignKey(Auto, on_delete=models.CASCADE, related_name='bookings')
    datetime_at = models.DateTimeField()
    datetime_to = models.DateTimeField()

    def __str__(self):
        return f"Booking {self.auto.plate} at {self.place}"
