import django 
import os
django.setup()
os.environ["DJANGO_SETTINGS_MODULE"] = "core.settings"


from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse, resolve
from model_bakery.baker import make
import pytz
from users.models import *
from .models import *
from .serializers import *
from .urls import *
from .views import *


# pip install pytz
# pip install model-bakery
# Run tests using: python manage.py test
# Run tests using: python manage.py test app_name.tests_module.TestClass


#==================================== Food Category Test =============================================

class FoodCategoryTests(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.category1 = FoodCategory.objects.create(category="Fruit", slug="fruit")
        self.category2 = FoodCategory.objects.create(category="Vegetable", slug="vegetable")
        # The args parameter provides the arguments needed by the URL pattern. In this case, it includes the primary key (id) of the FoodCategory instance.
        self.detail_url = reverse("food-categories-detail", args=[self.category1.id])
        self.list_url = reverse("food-categories-list")

    # Model Test
    def test_food_category_model(self):
        self.assertEqual(str(self.category1), "Fruit")
        self.assertEqual(self.category1.slug, "fruit")

    # Serializer Test
    def test_food_category_serializer(self):
        serializer = FoodCategorySerializer(self.category1)
        self.assertEqual(serializer.data["category"], "Fruit")
        self.assertEqual(serializer.data["slug"], "fruit")

    # View Test
    def test_list_food_categories(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Fruit")
        self.assertContains(response, "Vegetable")

    # View Detail Test
    def test_get_specific_category(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["category"], "Fruit")

    # URL Test
    def test_food_categories_url_resolves(self):
        # resolve function is used to match a URL string to the corresponding view function or class. It's helpful for testing that a specific URL correctly routes to the intended view.
        view = resolve("/api/v1/categories/")
        # view.func.cls: This accesses the view class that is resolved from the URL.
        self.assertEqual(view.func.cls, FoodCategoryModelViewSet)
        

#==================================== Food Category Test ===========================================

class FoodTests(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.category1 = FoodCategory.objects.create(category="Irani", slug="irani")
        self.food1 = Food.objects.create(food="Kebab", category=self.category1, price=420000, slug="kebab")
        self.food2 = Food.objects.create(food="Lobiapolp", category=self.category1, price=320000, slug="lobiapolp")
        self.detail_url = reverse("foods-detail", args=[self.food1.id])
        self.list_url = reverse("foods-list")
    
    # Model Test
    def test_food_model(self):
        self.assertEqual(str(self.food1), "Kebab")
        self.assertEqual(self.food1.slug, "kebab")
    
    # Serializer Test
    def test_food_serializer(self):
        serializer = FoodSerializer(self.food1)
        self.assertEqual(serializer.data["food"], "Kebab")
        self.assertEqual(serializer.data["slug"], "kebab")
        
    # View Test
    def test_list_foods(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Kebab")
        self.assertContains(response, "Lobiapolp")
    
    # View Detail Test
    def test_get_specific_food(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["food"], "Kebab")
        self.assertEqual(response.data["price"], 420000)
        
    # URL Test
    def test_food_url_resolve(self):
        view = resolve("/api/v1/foods/")
        self.assertEqual(view.func.cls, FoodModelViewSet)
        

#========================================= Review Test =====================================================

class ReviewTest(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        
        self.category_1 = FoodCategory.objects.create(category="Irani", slug="irani")
        self.food_1 = Food.objects.create(food="Kebab", category=self.category_1, price=420000, slug="kebab")
        self.food_2 = Food.objects.create(food="Lobiapolp", category=self.category_1, price=320000, slug="lobiapolp")
        self.user_1 = CustomUser.objects.create(first_name="Soheil", last_name="Daliri", email="soheil.dalirii@gmail.com")
        self.user_2 = CustomUser.objects.create(first_name="Ahmad", last_name="Rezaei", email="ahmad@gmail.com")
        self.user_1.set_password("abcABC123&")
        self.user_2.set_password("abcABC123&")
        self.user_1.save()
        self.user_2.save()
        self.client.force_authenticate(user=self.user_1) 
        
        self.comment_data_1 = Review.objects.create(food=self.food_1, user=self.user_1, review="گرونه", parent=None)
        self.comment_data_2 = Review.objects.create(food=self.food_1, user=self.user_2, review="نه، منصفانه است", parent=self.comment_data_1)
        self.comment_data_3 = {"food": self.food_2.id, "review": "خوشمزه بود", "parent": None}
         
        # Using kwargs in reverse is a way to dynamically build URLs with specific parameters, ensuring that tests and views are correctly linked to the intended resources. 
        self.url = reverse("review-list-create", kwargs={"food_id": self.food_1.id})

    def test_review_model(self):
        self.assertEqual(str(self.comment_data_1), f"{self.comment_data_1.id} ({self.user_1.first_name} {self.user_1.last_name})")
        self.assertEqual(self.comment_data_1.parent, None)
    
    def test_review_serializer(self):
        serializer = ReviewSerializer(instance=self.comment_data_2)
        serializer_data = serializer.data
        self.assertEqual(serializer_data["user"], self.comment_data_2.user.id)
        self.assertEqual(serializer_data["food"], self.comment_data_2.food.id)
        
    def test_fetch_reviews_view(self):
        response_1 = self.client.get(self.url)
        if response_1.status_code != status.HTTP_200_OK:
            print("Response Data: ", response_1.data)
        self.assertEqual(response_1.status_code, status.HTTP_200_OK)
        
    def test_leave_reviews_view(self):
        response_2 = self.client.post(self.url, self.comment_data_3, format="json")
        if response_2.status_code != status.HTTP_201_CREATED:
            print("Response Data: ", response_2.data)
        self.assertEqual(response_2.status_code, status.HTTP_201_CREATED)
        
    def test_review_url_resolve(self):
        view = resolve(f"/api/v1/reviews/{self.food_1.id}/")
        self.assertEqual(view.func.cls, ReviewAPIView)


#========================================= Review Delete Test =====================================================

class ReviewDeleteTest(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        
        self.category_1 = FoodCategory.objects.create(category="Irani", slug="irani")
        self.food_1 = Food.objects.create(food="Kebab", category=self.category_1, price=420000, slug="kebab")
        self.user_1 = CustomUser.objects.create(first_name="Soheil", last_name="Daliri", email="soheil.dalirii@gmail.com")
        self.user_1.set_password("abcABC123&")
        self.user_1.save()
        self.client.force_authenticate(user=self.user_1)  

        self.comment_data_1 = Review.objects.create(food=self.food_1, user=self.user_1, review="گرونه", parent=None)
        self.url = reverse("review-delete", kwargs={"review_id": self.comment_data_1.id})  

    def test_delete_reviews_view(self):
        response = self.client.delete(self.url)
        if response.status_code != status.HTTP_204_NO_CONTENT:
            print("Response Data: ", response.data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
    def test_review_delete_url_resolve(self):
        view = resolve(f"/api/v1/reviews/delete/{self.comment_data_1.id}/")
        self.assertEqual(view.func.cls, ReviewDeleteAPIView)

        
#========================================= Order Test ======================================================

class OrderTest(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user_1 = CustomUser.objects.create(first_name="Soheil", last_name="Daliri", email="soheil.dalirii@gmail.com")
        self.user_1.set_password("abcABC123&")
        self.user_1.save()
        
        self.category_1 = FoodCategory.objects.create(category="Irani", slug="irani")
        self.food_1 = Food.objects.create(food="Kebab", category=self.category_1, price=420000, slug="kebab")
        self.food_2 = Food.objects.create(food="Lobiapolp", category=self.category_1, price=320000, slug="lobiapolp")

        self.order = Order.objects.create(
            online_customer=self.user_1, 
            order_type="online",
            payment_method="online"
        )
        self.order_item_1 = OrderItem.objects.create(
            order=self.order, 
            food=self.food_1, 
            quantity=2, 
        )
        self.order_item_2 = OrderItem.objects.create(
            order=self.order, 
            food=self.food_2, 
            quantity=1, 
        )
        
        # It is used in your tests to simulate an authenticated user. It sets up the authentication for the test client, so when it makes requests, it includes the authenticated user's credentials.
        self.client.force_authenticate(user=self.user_1)
        self.url = reverse("place-orders")

    # Model Test
    def test_order_model(self):
        self.assertEqual(self.order.payment_amount(), self.food_1.price * 2 + self.food_2.price)
        self.assertEqual(str(self.order), f"Order {self.order.id} by {self.user_1} (Online)")

    # Serializer Test
    def test_order_serializer(self):
        # order = Order.objects.get(id=self.order.id)
        # serializer = OrderSerializer(order, context={'request': self.client})
        serializer = OrderSerializer(self.order)
        serialized_data = serializer.data
        self.assertNotIn("discount", serialized_data)
        self.assertNotIn("total_amount", serialized_data)  
        self.assertNotIn("discount_amount", serialized_data)  

    # View Test
    def test_place_order(self):
        data = {
            "order_items": [
                {"food": self.food_1.id, "quantity": 2},
                {"food": self.food_2.id, "quantity": 1}
            ],
            # "discount": "0gS3cMsdbP"
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("سفارش شما ثبت شد", response.data["message"])

    # URL Test
    def test_order_url_resolve(self):
        view = resolve("/api/v1/orders/")
        self.assertEqual(view.func.cls, OrderViewSet)


#==================================== Reservation Test =====================================================

class ReservationTest(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user_1 = CustomUser.objects.create(first_name="Soheil", last_name="Daliri", email="soheil.dalirii@gmail.com")
        self.user_1.set_password("abcABC123&")
        self.user_1.save()
        
        tz = pytz.timezone("Asia/Tehran")
        self.reservation_1 = Reservation.objects.create(
            user=self.user_1, 
            start_date=tz.localize(datetime(2024, 12, 10, 13, 30)), 
            end_date=tz.localize(datetime(2024, 12, 10, 19, 30)), 
            number_of_people=4, 
            number_of_tables=1
        )
        self.reservation_2 = Reservation.objects.create(
            user=self.user_1, 
            start_date=tz.localize(datetime(2024, 12, 11, 13, 30)),  
            end_date=tz.localize(datetime(2024, 12, 11, 19, 30)), 
            number_of_people=2, 
            number_of_tables=1
        )
        
        self.client.force_authenticate(user=self.user_1)
        self.url = reverse("make-reservations")

    # Model Test
    def test_reservation_model(self):
        self.assertEqual(str(self.reservation_1), "Reservation by Soheil Daliri at Pars Food")
        self.assertEqual(self.reservation_2.number_of_people, 2)

    # Serializer Test
    def test_reservation_serializer(self):
        serializer = ReservationSerializer(self.reservation_1)
        # The isoformat method is used to convert a date, time, or datetime object into a string in ISO 8601 format, which is an internationally accepted way to represent dates and times. 
        # This format is widely used in data interchange and ensures that the date and time are represented in a consistent and unambiguous way.
        # When you need to serialize a datetime object to a string format that is easy to store or transmit.
        # When interacting with APIs that expect dates and times in ISO 8601 format.
        self.assertEqual(serializer.data["start_date"], self.reservation_1.start_date.isoformat())
        self.assertEqual(serializer.data["number_of_tables"], 1)

    # View Test
    def test_make_reservation(self):
        data = {
            "start_date": "2024-12-13T13:30:00Z",  
            "end_date": "2024-12-13T19:30:00Z",
            "number_of_people": 3,
            "number_of_tables": 1,
            "description": "Birthday party"
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "درخواست رزرو شما ثبت شد، پس از تایید رستوان برای شما ایمیل تایید ارسال خواهد شد")

    # URL Test
    def test_reservation_url_resolve(self):
        view = resolve("/api/v1/reservations/")
        self.assertEqual(view.func.cls, ReservationViewSet)


# ==========================================================================================================
