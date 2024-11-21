from rest_framework import serializers
from .models import User, Auto, Parking, Place, Booking

class UserRegistrationSerializer(serializers.ModelSerializer):
    plate = serializers.CharField(max_length=15, required=True)
    certificate = serializers.CharField(max_length=255, required=True)
    color = serializers.CharField(max_length=50, required=True)
    brand = serializers.CharField(max_length=50, required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'role', 'plate', 'certificate', 'color', 'brand']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        plate = validated_data.pop('plate')
        certificate = validated_data.pop('certificate')
        color = validated_data.pop('color')
        brand = validated_data.pop('brand')

        # Создаём пользователя
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data['role']
        )

        # Создаём автомобиль
        Auto.objects.create(
            user=user,
            plate=plate,
            certificate=certificate,
            color=color,
            brand=brand
        )

        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class AutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auto
        fields = '__all__'


class ParkingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parking
        fields = '__all__'


from rest_framework import serializers
from .models import Place

class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ['id', 'is_free', 'number', 'parking']



class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
