from rest_framework import viewsets
from .models import User, Auto, Parking, Place, Booking
from .serializers import UserSerializer, AutoSerializer, ParkingSerializer, PlaceSerializer, BookingSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import timedelta
from django.utils.timezone import now


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


class ParkingViewSet(viewsets.ModelViewSet):
    queryset = Parking.objects.all()
    serializer_class = ParkingSerializer

    @action(detail=True, methods=['get'])
    def places(self, request, pk=None):
        """
        Получить все парковочные места по парковке
        """
        parking = self.get_object()
        places = parking.places.all()
        return Response(PlaceSerializer(places, many=True).data)


class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer

    @action(detail=True, methods=['post'])
    def book(self, request, pk=None):
        """
        Забронировать место по ID пользователя и ID места
        """
        place = self.get_object()
        user_id = request.data.get('user_id')
        auto_id = request.data.get('auto_id')

        if place.status != 'free':
            return Response({"error": "Place is not available for booking"}, status=400)

        try:
            user = User.objects.get(id=user_id)
            auto = Auto.objects.get(id=auto_id, user=user)
        except (User.DoesNotExist, Auto.DoesNotExist):
            return Response({"error": "Invalid user or auto ID"}, status=404)

        # Создаем бронирование
        booking = Booking.objects.create(
            place=place,
            auto=auto,
            datetime_at=now(),
            datetime_to=now() + timedelta(hours=1)  # Например, фиксированное время брони
        )

        # Обновляем статус места
        place.status = 'reserved'
        place.save()

        return Response(BookingSerializer(booking).data)



class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer