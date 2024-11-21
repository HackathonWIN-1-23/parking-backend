from rest_framework.routers import DefaultRouter
from .views import UserViewSet, AutoViewSet, ParkingViewSet, PlaceViewSet, BookingViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'autos', AutoViewSet)
router.register(r'parkings', ParkingViewSet)
router.register(r'places', PlaceViewSet)
router.register(r'bookings', BookingViewSet)

urlpatterns = router.urls
