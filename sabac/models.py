from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.timezone import now

class User(AbstractUser):
    email = models.EmailField(unique=True)
    Role_Choices = [
        ('saler' , 'Saler'),
        ('dealer' , 'Dealer'),
        ('inspector', 'Inspector'),
        ('admin' , 'Admin')
    ]
    role = models.CharField(max_length=20, choices=Role_Choices , default='saler')
    phone_number = models.CharField(max_length=20,unique=True, null=True,blank=True)
    adress = models.CharField(max_length=500)
    
    def __str__(self):
        return self.username
    
class Guest(models.Model):
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=30,unique=True)
    email = models.CharField(max_length=100,unique=True)
    
    def __str__(self):
        return f"{self.name}"
    
class saler_car_details(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('assigned','Assigned'),
        ('in_inspection', "In Inspection"),
        ('await_approval' , " Awating Approval"),
        ('rejected', 'Rejected'),
        ('bidding', 'In Bidding'),
        ('sold', 'Sold'),
    ]

    saler_car_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True, related_name='seller_cars')
    inspector = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_cars")  # New field
    guest = models.ForeignKey(Guest, on_delete=models.SET_NULL, null=True, related_name="guest_cars")  # Check this
    is_sold = models.BooleanField(default=False)
    car_name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    color = models.CharField(max_length=30)
    condition = models.CharField(max_length=1000)
    model = models.CharField(max_length=20)
    demand = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    city = models.CharField(max_length=100)
    milage = models.FloatField()
    description = models.TextField(blank=True, null=True)
    photos = models.JSONField(default=list, blank=True) 
    type = models.CharField(max_length=50)
    fuel_type = models.CharField(max_length=50)
    registered_in = models.CharField(max_length=100)
    engine_capacity = models.CharField(max_length=30)
    assembly = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20, null=True,blank=True)
    secondary_number = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    is_inspected = models.BooleanField(default=False)
    added_by = models.CharField(max_length=50, blank=True, null=True)  # Removed default


    def save(self, *args, **kwargs):
        """Automatically update `is_sold` if status changes to 'sold'."""
        
        if self.pk:
            existing_car = saler_car_details.objects.get(pk=self.pk)
            if existing_car.status == "pending" and self.status != "pending":
                self.is_inspected = True 
        
        
        
        
        if self.status == "sold":
            self.is_sold = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.car_name} ({self.model}) - {self.status}"
    
    # saler post images of car 
class CarPhoto(models.Model):
    car = models.ForeignKey(saler_car_details, on_delete=models.CASCADE, related_name='Photos')
    photo_base64 =models.TextField(null=False, blank=True)


    def __str__(self):
        return f"Photo of {self.car.car_name}"


# inspecor availability model
class Availability(models.Model):
    inspector = models.ForeignKey(
        settings.AUTH_USER_MODEL ,
        on_delete=models.CASCADE , 
        limit_choices_to={'role' : 'inspector'},
        related_name='inspector')
    date = models.DateField()
    time_slots = models.JSONField(default=list)
    
    def __str__(self):
        return f"{self.inspector.username} - {self.date}"
    
# saler select the time for inspection
class SelectedSlot(models.Model):
    saler_car = models.ForeignKey(
        saler_car_details ,
        on_delete=models.CASCADE ,null=True,blank=True,
        related_name='selected_slots')
    inspector = models.ForeignKey(
        settings.AUTH_USER_MODEL ,
        on_delete=models.CASCADE ,
        limit_choices_to={'role':'inspector'})
    date = models.DateField()
    time_slot = models.TimeField()
    BOOKED_BY_CHOICES = [
        ('seler', 'Seller'),
        ('inspector', 'Inspector'),
    ]
    booked_by = models.CharField(max_length=10, choices=BOOKED_BY_CHOICES, default='seller')
    
    
class InspectionReport(models.Model):
    inspector = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'inspector'})
    saler_car = models.ForeignKey(saler_car_details, on_delete=models.CASCADE, related_name='inspection_reports')
    
    # Car Details
    car_name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    color = models.CharField(max_length=30)
    condition = models.CharField(max_length=1000)
    model = models.CharField(max_length=20)
    car_photos = models.JSONField(default=list, null=True, blank=True)
    fuel_type = models.CharField(max_length=50)
    registry_number = models.CharField(max_length=100)
    year = models.IntegerField()
    engine_capacity = models.FloatField()
    mileage = models.FloatField()
    chassis_number = models.CharField(max_length=100)
    engine_type = models.CharField(max_length=100)
    transmission_type = models.CharField(max_length=50)

    # Inspection Ratings (1-100 scale)
    engine_condition = models.IntegerField(default=100)
    body_condition = models.IntegerField(default=100)
    clutch_condition = models.IntegerField(default=100)
    steering_condition = models.IntegerField(default=100)
    suspension_condition = models.IntegerField(default=100)
    brakes_condition = models.IntegerField(default=100)
    ac_condition = models.IntegerField(default=100)
    tyres_condition=models.IntegerField(default=100),
    electrical_condition = models.IntegerField(default=100)
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True) 
    saler_demand = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    overall_score = models.IntegerField(default=100)  # Average of all the conditions
    additional_comments = models.TextField(blank=True, null=True)
    inspection_date = models.DateTimeField(auto_now_add=True)
    
    
    # approve inspection
    def approve_inspection(self):
        if self.saler_car.status == "await_approval":
            self.saler_car.status = "bidding"
            self.saler_car.save()
            
            Notification.objects.create(
                recipient = self.saler_car.user,
                message = f"Your car {self.saler_car.car_name} has been Approved for bidding",
                saler_car = self.saler_car,
                category = "inspection_approved"
            )
    # reject inspection
    def reject_inspection(self):
        if self.saler_car.status == "await_approval":
            self.saler_car.status = "rejected",
            self.saler_car.save()
            
            Notification.objects.create(
                recipient = self.saler_car.user,
                message = f"Your car {self.saler_car.car_name} has been rejected for bidding",
                saler_car = self.saler_car,
                category = "inspection_rejected"
            )

    def __str__(self):
        return f"Inspection Report for {self.saler_car.car_name} by {self.inspector.username} on {self.inspection_date}"

    def save(self, *args, **kwargs):
        # Ensure all conditions are integers
        part_scores = [
            int(self.engine_condition), int(self.body_condition), int(self.clutch_condition),
            int(self.steering_condition), int(self.suspension_condition), int(self.brakes_condition),
            int(self.ac_condition), int(self.electrical_condition)
        ]
        
        # Calculate overall score
        self.overall_score = sum(part_scores) / len(part_scores)
        
        super().save(*args, **kwargs)
        
# Bidding model
class Bidding(models.Model):
    dealer = models.ForeignKey(User , on_delete=models.CASCADE , limit_choices_to={'role' : 'dealer'}, related_name='bids')
    saler_car = models.ForeignKey(saler_car_details, on_delete=models.CASCADE, related_name='bids')
    bid_amount = models.DecimalField(max_digits=100, decimal_places=2)
    bid_date = models.DateField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired')
    ], default='pending')
    
    def __str__(self):
        return f"Dealer :{self.dealer.username}"
    
# notification model for saler car posting
class Notification(models.Model):
    recipient = models.ForeignKey(User , on_delete=models.CASCADE, related_name='notifecation')
    bid = models.ForeignKey(Bidding, on_delete=models.CASCADE, null=True, blank=True, related_name="bid_acception" )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    saler_car = models.ForeignKey(saler_car_details,on_delete=models.CASCADE, related_name='notifications', null=True,blank=True)
    category = models.CharField(max_length=150, null=True, blank=True)
    
    def __str__(self):
        return f"Notifecation for {self.recipient.username} : {self.message[:20]}"
    
    
    
# notification wwhen inspection report posted by inspector
class InspectionReportNotification(models.Model):
    recepient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="inspection_notification")
    report = models.ForeignKey(InspectionReport, on_delete=models.CASCADE,related_name='notification')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    
#(Inspector assign slot to seller --manual entry)

class AssignSlot(models.Model):
    inspector = models.ForeignKey(
        User, on_delete=models.CASCADE, 
        limit_choices_to={'role': 'inspector'}, 
        related_name='assigning_slots'
    )
    car = models.ForeignKey(
        saler_car_details, on_delete=models.CASCADE, 
        related_name="assigned_slots"
    )  # ✅ Links slot to a specific car
    date = models.DateField()
    time_slot = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_by = models.CharField(max_length=50, default="inspector")  # ✅ Default to "inspector"


    def __str__(self):
        return f"Slot for {self.car.car_name} ({self.car.model}) on {self.date} at {self.time_slot}"


# class AssignSlot(models.Model):
#     inspector = models.ForeignKey(
#         User, on_delete=models.CASCADE, 
#         limit_choices_to={'role': 'inspector'}, 
#         related_name='assigning_slot'
#     )
#     seller_name = models.CharField(max_length=255)
#     seller_phone = models.CharField(max_length=20)
#     seller_email = models.EmailField()
#     car_company = models.CharField(max_length=100)
#     car_model = models.CharField(max_length=100)
#     car_name = models.CharField(max_length=100)
#     car_photos = models.JSONField(default=list,null=True,blank=True)  
#     date = models.DateField()
#     time_slot = models.TimeField()
#     booked_by = models.CharField(max_length=20, default="Inspector")
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def save_car_photos(self, base64_list):
#         """Ensures car_photos is always stored as a valid JSON list"""
#         if isinstance(base64_list, list):
#             self.car_photos = base64_list
#         else:
#             self.car_photos = []
#         self.save()
        
        
# for inspection saler name and number
class AdditionalDetails(models.Model):
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=30)
    
    def __str__(self):
        return f"{self.name}"
    


    
    
