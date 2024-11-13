from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from django.http import JsonResponse
from .models import *
from .serializers import *
from custom_permission import * 

#==================================== admin View ======================================================

# def calculate_price(request):
#     start_date = request.GET.get('start_date')
#     end_date = request.GET.get('end_date')
#     number_of_tables = int(request.GET.get('number_of_tables', 0))

#     if start_date and end_date and number_of_tables:
#         start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M")
#         end_date = datetime.strptime(end_date, "%Y-%m-%dT%H:%M")
#         duration = (end_date - start_date).total_seconds() / 3600
#         price = (number_of_tables * duration) * 50000
#         return JsonResponse({'price': price})
#     return JsonResponse({'price': 0})


def get_food_price(request, food_id):
    try:
        food = Food.objects.get(id=food_id)
        return JsonResponse({'price': food.price})
    except Food.DoesNotExist:
        return JsonResponse({'error': 'Food item not found'}, status=404)



# HTML Select Element: Each food item in your form has a <select> element with options. 
# Each option has a value attribute that corresponds to the food_id.
# JavaScript Fetch Request: When a food item is selected, the value of the <select> element 
# (which is the food_id) is used in the fetch request URL.
# Django View: The fetch request is sent to the Django view get_food_price, which takes food_id as a parameter. 
# The view retrieves the food item from the database using food_id and returns its price as a JSON response.

# User selects a food item.
# JavaScript captures the food_id from the <select> element.
# JavaScript sends a fetch request to /get_food_price/${food_id}/.
# Django view get_food_price processes the request and returns the price.


    
#==================================== Food Category View ===================================================

class FoodCategoryModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = FoodCategory.objects.all().order_by("parent")
    serializer_class = FoodCategorySerializer
    http_method_names = ["get"]
    pagination_class = PageNumberPagination
    filter_backends = [SearchFilter]
    search_fields = ["id", "slug"]
    
    # This means the action applies to the entire collection and does not include a lookup field in the URL.
    # url_path allows you to create custom and dynamic URLs that can handle specific actions like fetching each category item by its slug.
    @action(detail=False, methods=["get"], url_path="slug/(?P<slug>[^/.]+)")
    def get_by_slug(self, request, slug=None):
        try:
            category = FoodCategory.objects.get(slug=slug)
            serializer = self.get_serializer(category)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except FoodCategory.DoesNotExist:
            return Response({"message": "پیدا نشد."}, status=status.HTTP_404_NOT_FOUND)
    
# class FoodCategoryGenericsView(generics.ListAPIView):
#     permission_classes = [IsAuthenticatedOrReadOnly]
#     queryset = FoodCategory.objects.all().order_by("parent")
#     serializer_class = FoodCategorySerializer
#     pagination_class = PageNumberPagination
#     filter_backends = [SearchFilter]
#     search_fields = ["id", "slug"] 
    
    
#==================================== Food View ============================================================

class FoodModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Food.objects.filter(is_active=True).order_by("-price")
    serializer_class = FoodSerializer
    http_method_names = ["get"]
    pagination_class = PageNumberPagination
    filter_backends = [SearchFilter]
    search_fields = ["id", "slug"]
    
    @action(detail=False, methods=["get"], url_path="slug/(?P<slug>[^/.]+)")
    def get_by_slug(self, request, slug=None):
        try:
            food = Food.objects.get(slug=slug, is_active=True)
            serializer = self.get_serializer(food)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Food.DoesNotExist:
            return Response({"message": "پیدا نشد."}, status=status.HTTP_404_NOT_FOUND)


# class FoodGenericsView(generics.ListAPIView):
#     permission_classes = [IsAuthenticatedOrReadOnly]
#     queryset = Food.objects.filter(is_active=True).order_by("-price")
#     serializer_class = FoodSerializer
#     pagination_class = PageNumberPagination
#     filter_backends = [SearchFilter]
#     search_fields = ["id", "slug"] 


#====================================== Review View ========================================================

class ReviewAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        request=ReviewSerializer,
        responses={201: ReviewSerializer}
    )
    def get(self, request, food_id):
        # parent__isnull fetches comments without a parent.
        top_level_reviews = Review.objects.filter(food_id=food_id, parent__isnull=True, is_active=True)
        reviews_data = []

        for review in top_level_reviews:
            review_serializer = ReviewSerializer(review)
            # It fetches replies separately and includes them in the response.
            replies = Review.objects.filter(parent=review, is_active=True)
            replies_serializer = ReviewSerializer(replies, many=True)
            reviews_data.append({
                "review": review_serializer.data,
                "replies": replies_serializer.data
            })

        return Response(reviews_data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ReviewSerializer,
        responses={201: ReviewSerializer}
    )
    def post(self, request, food_id):
        serializer = ReviewSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(food_id=food_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewDeleteAPIView(APIView):
    permission_classes = [UserCheckOut]

    @extend_schema(
        request=ReviewSerializer,
        responses={204: ReviewSerializer}
    )
    def delete(self, request, review_id):
        try:
            review = Review.objects.get(id=review_id)
            self.check_object_permissions(request, review)
            review.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Review.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


#==================================== Online Order View ====================================================

class OrderViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request = OrderSerializer,
        responses = {201: OrderSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            response_data = serializer.save()
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class Orderbasename(viewsets.ModelViewSet):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated]
#     http_method_names = ["post"]

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
    
#     def perform_create(self, serializer):
#         serializer.save()



# {
#     "discount": "V0TQwyGZru",
#     "order_items": [
#         {
#             "food": 9,
#             "quantity": 2
#         },
#         {
#             "food": 2,
#             "quantity": 2
#         },
#         {
#             "food": 3,
#             "quantity": 1
#         }
#     ]
# }

# {
#     "order_items": [
#         {
#             "food": 5,
#             "quantity": 3
#         },
#         {
#             "food": 2,
#             "quantity": 2
#         }
#     ]
# }


#==================================== Reservation View =====================================================

class ReservationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request = ReservationSerializer,
        responses = {201: ReservationSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = ReservationSerializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer, request)
            return Response({"message": "درخواست رزرو شما ثبت شد، پس از تایید رستوان برای شما ایمیل تایید ارسال خواهد شد"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # The `perform_create` method is a hook provided by DRF that allows you to customize the creation of an instance.
    # It is called by the `create` method of the viewset after the serializer's `is_valid` method has been called and before the instance is saved.
    # This approach keeps your serializer clean and focused on validation and data transformation, while the view handles the logic related to the request context.
    def perform_create(self, serializer, request):
        serializer.save(user=request.user)

            
# {
#     "start_date": "2024-11-10 19:30:00.000000",
#     "end_date": "2024-11-10 22:30:00.000000",
#     "number_of_people": 6,
#     "number_of_tables": 2
# }


# ==========================================================================================================
