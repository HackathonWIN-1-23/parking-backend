from rest_framework import viewsets
from .models import User, Auto, Parking, Place, Booking
from .serializers import UserSerializer, AutoSerializer, ParkingSerializer, PlaceSerializer, BookingSerializer
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from django.utils.dateparse import parse_datetime
from rest_framework.permissions import AllowAny



# api/views.py
from rest_framework.views import APIView
from rest_framework import status
from .serializers import UserRegistrationSerializer

class AvailablePlacesView(ListAPIView):
    serializer_class = PlaceSerializer


    def get_queryset(self):
        parking_id = self.request.query_params.get('parking')
        start_time = parse_datetime(self.request.query_params.get('start_time'))
        end_time = parse_datetime(self.request.query_params.get('end_time'))

        # Фильтрация доступных мест
        return Place.objects.filter(
            parking_id=parking_id,
            is_free=True
        ).exclude(
            bookings__datetime_at__lt=end_time,
            bookings__datetime_to__gt=start_time
        )


class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


    @action(detail=True, methods=['get'])
    def autos(self, request, pk=None):
        """
        Получить все машины определенного пользователя
        """
        user = self.get_object()
        autos = user.autos.all()
        return Response(AutoSerializer(autos, many=True).data)

    @action(detail=True, methods=['get'])
    def bookings(self, request, pk=None):
        """
        Получить все брони определенного пользователя
        """
        user = self.get_object()
        bookings = Booking.objects.filter(auto__user=user)
        return Response(BookingSerializer(bookings, many=True).data)


class AutoViewSet(viewsets.ModelViewSet):
    queryset = Auto.objects.all()
    serializer_class = AutoSerializer
    permission_classes = [IsAuthenticated]


class ParkingViewSet(viewsets.ModelViewSet):
    queryset = Parking.objects.all()
    serializer_class = ParkingSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def places(self, request, pk=None):
        """
        Получить все парковочные места по парковке
        """
        parking = self.get_object()
        places = parking.places.all()
        return Response(PlaceSerializer(places, many=True).data)


from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Place, Booking, User, Auto
from .serializers import PlaceSerializer, BookingSerializer
from django.utils.timezone import now
from datetime import timedelta

class PlaceViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления парковочными местами.
    """
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer

    @action(detail=False, methods=['get'])
    def free_places(self, request):
        """
        Получить список всех свободных мест.
        """
        free_places = Place.objects.filter(is_free=True)
        serializer = self.get_serializer(free_places, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_parking(self, request):
        """
        Получить места для определенной парковки (по parking_id).
        """
        parking_id = request.query_params.get('parking_id')
        if not parking_id:
            return Response({"error": "Parking ID is required"}, status=400)

        places = Place.objects.filter(parking_id=parking_id)
        serializer = self.get_serializer(places, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def book(self, request, pk=None):
        """
        Забронировать место (по ID места).
        """
        place = self.get_object()
        if not place.is_free:
            return Response({"error": "Place is already reserved"}, status=400)

        user_id = request.data.get('user_id')
        auto_id = request.data.get('auto_id')

        try:
            user = User.objects.get(id=user_id)
            auto = Auto.objects.get(id=auto_id, user=user)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        except Auto.DoesNotExist:
            return Response({"error": "Auto not found or not owned by this user"}, status=404)

        # Проверяем, есть ли у пользователя активное бронирование
        active_booking = Booking.objects.filter(auto__user=user, place__is_free=False).exists()
        if active_booking:
            return Response({"error": "User already has an active booking"}, status=400)

        # Создаем бронирование
        booking = Booking.objects.create(
            place=place,
            auto=auto,
            datetime_at=now(),
            datetime_to=now() + timedelta(hours=1)  # Фиксированное время бронирования
        )

        # Обновляем статус места
        place.is_free = False
        place.save()

        return Response(BookingSerializer(booking).data, status=201)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Отменить бронирование для места.
        """
        place = self.get_object()
        try:
            booking = Booking.objects.get(place=place, place__is_free=False)
        except Booking.DoesNotExist:
            return Response({"error": "No active booking for this place"}, status=404)

        # Удаляем бронирование и освобождаем место
        booking.delete()
        place.is_free = True
        place.save()

        return Response({"message": "Booking canceled successfully"}, status=200)


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
