from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from uuid import uuid4
from django.conf import settings
from os import path
from users.models import InPersonCustomer


#======================================= Needed Method ======================================================

def upload_to(instance, filename):
    try:
        file_name, ext = path.splitext(filename)
        new_filename = f"{uuid4()}{ext}"
        # model = instance.category if instance.category else instance.food
        # The getattr function retrieves the value of an attribute from an object. It's super useful when you're working with dynamic attribute names.
        model = getattr(instance, "category", None) or getattr(instance, "food", None) or getattr(instance, "gallery", "default_gallery")
        if isinstance(instance, FoodCategory):
            return f"images/categories/{model}/{new_filename}"
        elif isinstance(instance, Food):
            return f"images/foods/{model}/{new_filename}"
        elif isinstance(instance, Gallery):
            return f"images/gallery/{model}/{new_filename}"
        else:
            return f"images/others/{new_filename}"
    except AttributeError:
        return f"images/others/{new_filename}"
    

#==================================== Food Category Model ===================================================

class FoodCategory(models.Model):
    category = models.CharField(max_length=100, verbose_name="Category")
    parent = models.ForeignKey("FoodCategory", on_delete=models.CASCADE, blank=True, null=True, related_name="FoodCategory_parents", verbose_name="Parent") 
    slug = models.SlugField(unique=True, blank=True, null=True, verbose_name="Slug")
    image = models.ImageField(upload_to=upload_to, verbose_name="Image")

    def __str__(self):
        return f"{self.category}"
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["parent"]),
            models.Index(fields=["slug"]),
        ]
 
        
#==================================== Food Model ===========================================================

class Food(models.Model):
    food = models.CharField(max_length=100, verbose_name="Food")
    category = models.ForeignKey(FoodCategory, on_delete=models.CASCADE, related_name="Food_categories", verbose_name="Category")
    price = models.PositiveIntegerField(default=0, verbose_name="Price")
    slug = models.SlugField(unique=True, blank=True, null=True, verbose_name="Slug")
    ingredient = models.TextField(blank=True, null=True, verbose_name="Ingredient")
    is_active = models.BooleanField(default=True, verbose_name="Being Active")
    image = models.ImageField(upload_to=upload_to, verbose_name="Image")
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, editable=False, verbose_name="Updated at")

    def __str__(self):
        return f"{self.food}"
    
    class Meta:
        verbose_name = "Food"
        verbose_name_plural = "Foods"
        indexes = [
            models.Index(fields=["food"]),
            models.Index(fields=["category"]),
            models.Index(fields=["price"]),
            models.Index(fields=["slug"]),
        ]
  
        
#==================================== Gallery Model ========================================================

class Gallery(models.Model):
    gallery = models.ForeignKey(Food, on_delete=models.CASCADE, related_name="galleries_Gallery", verbose_name="Food")
    image = models.ImageField(upload_to=upload_to, verbose_name="Image")

    def __str__(self):
        return f"{self.gallery}"
    
    class Meta:
        verbose_name = "Gallery"
        verbose_name_plural = "Galleries"

       
#==================================== Discount Model =======================================================

class Discount(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name="Code")
    percentage = models.IntegerField(validators=[MinValueValidator(10),MaxValueValidator(50)], verbose_name="Percentage")
    is_active = models.BooleanField(default=False, verbose_name="Being Active")
    start_date = models.DateTimeField(verbose_name="Start Date")
    expiry_date = models.DateTimeField(verbose_name="Expiry Date")
    
    def __str__(self):
        return f"{self.code} has {self.percentage} off, from {self.start_date} to {self.expiry_date}"
    
    @staticmethod
    def code_generator(count):
        from string import ascii_letters, digits
        from random import choice
        characters = list(ascii_letters + digits)
        code_list = [choice(characters) for _ in range(count)]
        return "".join(code_list)
    
    def clean(self):
        if not self.code:
            self.code = self.code_generator(10)
    
    def save(self, *args, **kwargs):
        self.full_clean()  
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Discount"
        verbose_name_plural = "Discounts"
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["start_date"]),
            models.Index(fields=["expiry_date"]),
        ]

      
#==================================== Order Model ==========================================================
   
class Order(models.Model):
    ORDER_TYPE_CHOICES = [("in_person", "In-Person"), ("online", "Online")]
    PAYMENT_METHOD_CHOICES = [("cash", "Cash"), ("credit_card", "Credit-Card"), ("online", "Online")]
    PAYMENT_STATUS_CHOICES = [("pending", "Pending"), ("completed", "Completed"), ("failed", "Failed")]
    
    online_customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name="Order_online_customers", verbose_name="Online Customer")
    in_person_customer = models.ForeignKey(InPersonCustomer, on_delete=models.CASCADE, blank=True, null=True, related_name="Order_in_person_customers", verbose_name="In-Person Customer")
    food_items = models.ManyToManyField(Food, through="OrderItem", verbose_name="Food Items")
    total_amount = models.PositiveIntegerField(default=0, verbose_name="Total Amount")
    discount_amount = models.PositiveIntegerField(default=0, verbose_name="Discount Amount")
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES, verbose_name="Order Type")
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHOD_CHOICES, verbose_name="Payment Method")
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default="pending", verbose_name="Payment Status")
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name="Created at")

    def __str__(self):
        customer = self.online_customer if self.online_customer else self.in_person_customer
        return f"Order {self.id} by {customer} ({self.get_order_type_display()})" if customer else f"Order {self.id} ({self.get_order_type_display()})"

    def customer(self):
        customer = self.online_customer if self.online_customer else self.in_person_customer
        return customer
    
    def payment_amount(self):
        return self.total_amount + self.discount_amount
    
    def clean(self):
        self.validate_customer()
        self.completed_payment()
    
    def validate_customer(self):
        if not self.online_customer and not self.in_person_customer:
            raise ValidationError("customer is required.")
    
    def calculate_order_items(self):
        order_items = OrderItem.objects.filter(order=self)
        self.total_amount = sum(item.grand_total for item in order_items)
        # self.save(update_fields=["total_amount"])
    
    def completed_payment(self):
        if self.payment_method is not None:
            self.payment_status = "completed"
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        self.calculate_order_items()              

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        # This will create database indexes on the specified fields, which can help speed up queries involving these fields.
        indexes = [
            models.Index(fields=["order_type"]),
            models.Index(fields=["payment_method"]),
            models.Index(fields=["payment_status"]),
            models.Index(fields=["created_at"]),
        ]

        
        
#==================================== Order Item Model ======================================================

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="OrderItem_orders", verbose_name="Order")
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name="OrderItem_foods", verbose_name="Food")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantity")
    grand_total = models.PositiveIntegerField(verbose_name="Grand Total")
    
    def __str__(self):
        return f"{self.food} x {self.quantity}"
    
    def item_price(self):
        return self.food.price

    def calculate_orders(self):
        self.grand_total = self.item_price() * self.quantity
    
    def save(self, *args, **kwargs):
        self.calculate_orders()
        super().save(*args, **kwargs)
        
    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        indexes = [
            models.Index(fields=["food"]),
            models.Index(fields=["order"]),
        ]
        

#==================================== Review Model =========================================================

class Review(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name="Review_foods", verbose_name="Food")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="Review_users", verbose_name="User")
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name="Review_admins", verbose_name="Admin")
    review = models.TextField(verbose_name="Review")
    parent = models.ForeignKey("Review", on_delete=models.CASCADE, blank=True, null=True, related_name="Review_parent", verbose_name="Parent")
    is_active = models.BooleanField(default=False, verbose_name="Being Active")
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name="Created at")
    
    def __str__(self):
        return f"{self.id} ({self.user})"
    
    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"


#==================================== Holiday Model =========================================================

class Holiday(models.Model):
    date = models.DateField(verbose_name="Holiday Date")
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="Description")

    def __str__(self):
        return f"Holiday on {self.date}"
    
    class Meta:
        verbose_name = "Holiday"
        verbose_name_plural = "Holidays"
        
        
#==================================== Reservation Model ====================================================
        
class Reservation(models.Model):
    ORDER_TYPE_STATUS = [("pending", "Pending"), ("approved", "Approved"), ("expired", "Expired"),]
    TOTAL_TABLES = 12
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="Reservation_users", verbose_name="User")
    start_date = models.DateTimeField(verbose_name="Start Date")
    end_date = models.DateTimeField(verbose_name="End Date")
    number_of_people = models.IntegerField(verbose_name="Number Of People")
    number_of_tables = models.IntegerField(verbose_name="Number Of Tables")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    reservation_date = models.DateTimeField(auto_now_add=True, editable=False, verbose_name="Reservation Date")
    price = models.PositiveIntegerField(default=0, editable=False, verbose_name="Price")
    is_approved = models.BooleanField(default=False, verbose_name="Being Approved")
    order_status = models.CharField(max_length=10, choices=ORDER_TYPE_STATUS, default="pending", verbose_name="Order Status")
    approved_date = models.DateTimeField(blank=True, null=True, editable=False, verbose_name="Approved Date")

    def __str__(self):
        return f"Reservation by {self.user.first_name} {self.user.last_name} at Pars Food"
    
    def get_available_tables(self):
        # start_date__lt: This translates to start_date < self.end_date, where lt stands for "less than".
        # start_date__lt=self.end_date: Start before the end date of the current reservation.
        # end_date__gt: This means end_date > self.start_date, with gt standing for "greater than".
        # end_date__gt=self.start_date: End after the start date of the current reservation.
        # exclude(id=self.id): Excludes the current reservation to avoid double-counting.
        overlapping_reservations = Reservation.objects.filter(start_date__lt=self.end_date, end_date__gt=self.start_date, is_approved=True).exclude(id=self.id)
        reserved_tables = sum(reservation.number_of_tables for reservation in overlapping_reservations)
        available_tables = self.TOTAL_TABLES - reserved_tables
        return available_tables
    
    def clean(self):
        self.validate_times()
        self.validate_tables()
        self.validate_approval()
        self.validate_holiday()
           
    def validate_times(self):
        start_time = datetime.strptime("12:00:00", "%H:%M:%S").time()
        end_time = datetime.strptime("11:59:59", "%H:%M:%S").time()
        if self.start_date is None or self.end_date is None:
            raise ValidationError("Start date and end date must be specified.")
        if start_time > self.start_date.time():
            raise ValidationError("Start time must be after 12:00 PM.")
        if end_time >= self.end_date.time():
            raise ValidationError("End time must be before 12:00 PM.")
      
    def validate_tables(self): 
        available_tables = self.get_available_tables()
        
        if self.number_of_tables is None:
            raise ValidationError("Number of tables must be specified.")
        if self.number_of_tables > available_tables:
            raise ValidationError(f"Only {available_tables} tables are available for the requested time period.")
        if self.number_of_tables <= 0:
            raise ValidationError("Number of tables must be greater than zero.")
         
    def validate_approval(self):
        if self.is_approved and self.approved_date is None:
            self.approved_date = timezone.now()
            
    # def validate_holiday(self):
    #     holidays = Holiday.objects.values_list("date", flat=True)     
    #     if self.start_date.date() in holidays or self.end_date.date() in holidays:
    #         raise ValidationError(f"Reservations cannot be made on Holidays.")
    
    def validate_holiday(self):
        holidays = Holiday.objects.all()
        for holiday in holidays:
            if self.start_date.date() == holiday.date or self.end_date.date() == holiday.date:
                raise ValidationError(f"Reservations cannot be made on {holiday.description}.")
    
    def calculate_price(self):
        table_per_hour = 50000
        duration = (self.end_date - self.start_date).total_seconds() / 3600  
        self.price = (self.number_of_tables * duration) * table_per_hour
    
    def save(self, *args, **kwargs):
        self.full_clean()
        self.calculate_price()
        super().save(*args, **kwargs)
        
    class Meta:
        verbose_name = "Reservation"
        verbose_name_plural = "Reservations"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["start_date"]),
            models.Index(fields=["end_date"]),
            models.Index(fields=["number_of_tables"]),
            models.Index(fields=["is_approved"]),
            models.Index(fields=["order_status"]),
        ]
        
            
# ==========================================================================================================

# The second approach of placing orders with two different models which uses The GenericForeignKey to handle this.


# from django.contrib.contenttypes.fields import GenericForeignKey
# from django.contrib.contenttypes.models import ContentType

# class InPersonOrder(models.Model):
#     PAYMENT_METHOD_CHOICES = [("cash", "Cash"), ("credit_card", "Credit-Card"),]
#     PAYMENT_STATUS_CHOICES = [("pending", "Pending"), ("completed", "Completed"), ("failed", "Failed"),]
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     food_items = models.ManyToManyField("Food", through='OrderItem')
#     total_amount = models.DecimalField(max_digits=10, decimal_places=2)
#     payment_method = models.CharField(max_length=15, choices=PAYMENT_METHOD_CHOICES) 
#     payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES)   
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"In-Person Order {self.id} by {self.user}"


# class OnlineOrder(models.Model):
#     PAYMENT_METHOD_CHOICES = [("cash", "Cash"), ("credit_card", "Credit-Card"),]
#     PAYMENT_STATUS_CHOICES = [("pending", "Pending"), ("completed", "Completed"), ("failed", "Failed"),]
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     food_items = models.ManyToManyField("Food", through="OrderItem")
#     total_amount = models.DecimalField(max_digits=10, decimal_places=2)
#     payment_method = models.CharField(max_length=15, choices=PAYMENT_METHOD_CHOICES) 
#     payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES)   
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Order {self.id} by {self.user}"


# class OrderItem(models.Model):
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE) # will store the type of the related model (InPersonOrder or OnlineOrder)
#     object_id = models.PositiveIntegerField() # will store the ID of the related order instance
#     # The GenericForeignKey (order) will combine these two fields to create a reference to either an InPersonOrder or an OnlineOrder
#     order = GenericForeignKey("content_type", "object_id")
#     food = models.ForeignKey("Food", on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)
#     price = models.DecimalField(max_digits=10, decimal_places=2)

#     def __str__(self):
#         return f"{self.food} x {self.quantity}"
    
    
# ==========================================================================================================


