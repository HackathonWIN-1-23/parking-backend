from rest_framework.routers import DefaultRouter
from .views import UserViewSet, AutoViewSet, ParkingViewSet, PlaceViewSet, BookingViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path, include
from .views import UserRegistrationView, AvailablePlacesView


router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'autos', AutoViewSet)
router.register(r'parkings', ParkingViewSet)
router.register(r'places', PlaceViewSet)
router.register(r'bookings', BookingViewSet)

urlpatterns = [
    path('available-places/', AvailablePlacesView.as_view(), name='available-places'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]
