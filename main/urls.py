from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from .views import (get_food_price, FoodCategoryModelViewSet, 
                    FoodModelViewSet, OrderViewSet, ReservationViewSet, ReviewAPIView, ReviewDeleteAPIView)

router = DefaultRouter()
router.register(r"categories", FoodCategoryModelViewSet, basename="food-categories")
router.register(r"foods", FoodModelViewSet, basename="foods")
# router.register(r"orders", OrderViewSet, basename="place-orders")
# router.register(r"order", OrderModelViewSet, basename="place-an-order")
# router.register(r"reservations", ReservationViewSet, basename="make-reservations")


urlpatterns = [
    # path('calculate_price/', calculate_price, name='calculate_price'),
    path("get_food_price/<int:food_id>/", get_food_price, name="get_food_price"),
    path("reviews/<int:food_id>/", ReviewAPIView.as_view(), name="review-list-create"),
    path("reviews/delete/<int:review_id>/", ReviewDeleteAPIView.as_view(), name="review-delete"),
    path("orders/", OrderViewSet.as_view({"post": "create"}), name="place-orders"), 
    path("reservations/", ReservationViewSet.as_view({"post": "create"}), name="make-reservations"), 
    # path("food-categories/", FoodCategoryGenericsView.as_view(), name="food_category"),
    # path("food/", FoodGenericsView.as_view(), name="food"), 
]


urlpatterns += router.urls
