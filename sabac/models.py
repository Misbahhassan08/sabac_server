import copy
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from sabac.notification_service import send_notification


class User(AbstractUser):
    email = models.EmailField(unique=True)
    Role_Choices = [
        ("saler", "Saler"),
        ("dealer", "Dealer"),
        ("inspector", "Inspector"),
        ("admin", "Admin"),
    ]
    role = models.CharField(max_length=20, choices=Role_Choices, default="saler")
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    adress = models.CharField(max_length=500)
    image = models.CharField(max_length=500, null=True, blank=True)
    plain_password = models.CharField(max_length=100,null=True,blank=True)
    google_token = models.CharField(max_length=500, null=True, blank=True) 


    def __str__(self):
        return self.username



OPTION_CHOICES = [
    ("basic", "BASIC"),
    ("mid_option", "MID OPTION"),
    ("full_option", "FULL OPTION"),
    ("i_dont_know", "I DONT KNOW"),
]
PAINT_CHOICES = [
    ("original_paint", "ORIGINAL PAINT"),
    ("partial_repaint", "PARTIAL REPAINT"),
    ("full_repaint", "FULL REPAINT"),
    ("i_dont_know", "I DONT KNOW"),
]
SPECIFICATON_OPTIONS = [
    ("gcc_specs", "GCC SPECS"),
    ("non_specs", "NON SPECS"),
    ("i_dont_know", "I DONT KNOW"),
]
# SPECIFICATON_OPTIONS = [
#     ("mid_option", "Mid Option"),
#     ("full_option", "Full Option"),
#     ("sport_package", "Sport Package"),
#     ("luxury_package", "Luxury Package"),
#     ("tech_package", "Tech Package"),
#     ("single_owner", "Single Owner"),
#     ("company_maintained", "Company Maintained"),
# ]

class saler_car_details(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("assigned", "Assigned"),
        ("in_inspection", "In Inspection"),
        ("await_approval", "Awaiting Approval"),
        ("rejected", "Rejected"),
        ("bidding", "In Bidding"),
        ("expired", "Expired"),
        ("in_inventory" , "In Inventory"),
        ("sold", "Sold"),
    ]

    saler_car_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="owner_car"
    )
    inspector = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inspector_connected",
    )  # New field
    winner_dealer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dealer_inventory_cars",
    )
    is_sold = models.BooleanField(default=False)
    car_name = models.CharField(max_length=100)
    car_variant = models.CharField(max_length=100,null=True,blank=True)
    company = models.CharField(max_length=100)
    year = models.CharField(max_length=20)
    engine_size = models.CharField(max_length=20)
    milage = models.CharField(max_length=100)
    option_type = models.CharField(max_length=50, choices=OPTION_CHOICES)
    paint_condition = models.CharField(max_length=100, choices=PAINT_CHOICES)
    specs = models.CharField(max_length=100, choices=SPECIFICATON_OPTIONS)
    photos = models.JSONField(null=True, blank=True)
    primary_phone_number = models.CharField(max_length=15, null=True, blank=True)
    secondary_phone_number = models.CharField(max_length=15, null=True, blank=True)
    inspection_date = models.DateField(null=True, blank=True)
    inspection_time = models.CharField(max_length=20 , null=True , blank=True) ##change 15/5/2025
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")
    is_inspected = models.BooleanField(default=False)
    added_by = models.CharField(max_length=50, blank=True, null=True)
    is_manual = models.BooleanField(default=False)
    is_booked = models.BooleanField(default=False)
    bidding_start_time = models.DateTimeField(null=True, blank=True)
    bidding_end_time = models.DateTimeField(null=True, blank=True)
    demand= models.DecimalField(max_digits=60, decimal_places=2, null=True,blank=True)
    min_bid_amount  = models.DecimalField(max_digits=60,decimal_places=2,null=True,blank=True)



    # def start_bidding(self):
    #     self.bidding_start_time = timezone.now()
    #     self.bidding_end_time = self.bidding_start_time + timedelta(days=10)
    #     self.save()

    def is_bidding_active(self):
        now_time = timezone.now()
        return (
            self.bidding_start_time
            and self.bidding_end_time
            and self.bidding_start_time <= now_time <= self.bidding_end_time
        )

    
    def save(self, *args, **kwargs):
        now_time = timezone.now()
        was_expired = self.status == "expired"

        # Mark sold
        if self.status == "sold":
            self.is_sold = True

        # Auto-expire if bidding time passed
        if (
            self.status == "bidding"
            and self.bidding_end_time
            and now_time > self.bidding_end_time
            and not self.is_sold
        ):
            self.status = "expired"

        super().save(*args, **kwargs)
        
        # == send notofocation only when newly expires
        if self.status == "expired" and not was_expired:
            car_info = f"{self.company} {self.car_name} {self.car_variant}"
            
            # ====notify Owner=====
            # if self.user:
            #     message = f"Your {car_info} has been expired"
                
            #     Notification.objects.create(
            #     recipient=self.user,
            #     message=message,
            #     saler_car=self,
            #     category="seller_car_expired",
            # )
            # send_notification(
            #     title="Car Expired",
            #     body=message,
            #     user=self.user,
            # )
            
            # geting user model
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # ===Notify dealers===
            dealers = User.objects.filter(role="dealer")
            
            # sample message for dealer
            message = f"The bidding period of {car_info} has been ended."
            
            for dealer in dealers:
                Notification.objects.create(
                    recipient=dealer,
                    message = message,
                    saler_car = self,
                    category="dealer_car_expied"
                )
            # ===push notification Dealer ===
                send_notification(title="Car Expired" , body=message , user=dealer,
                    more_detail={
                    "car_type": "seller",
                    "car_id": str(self.saler_car_id),
                    "car_name": self.car_name,
                    "tab": "expire",
                })
                print(f"[✅ Dealer Notified] Dealer ID: {dealer.id} - {dealer.email} for Car: {car_info}")

            
            # ===notifiy Admin===
            
            # --get all admins from model--
            admins = User.objects.filter(role="admin")
            
            # ---sample message--
            message = f"{car_info} has been expired. No winning Bid"
            
            for admin in admins:
                Notification.objects.create(
                    recipient = admin,
                    message = message,
                    saler_car= self,
                    category = "admin_car_expired" 
                )
                send_notification(title="Car Expired", body=message, user=admin,more_detail={
                    "car_type": "seller",
                    "car_id": str(self.saler_car_id),
                    "car_name": self.car_name,
                    "tab": "expire",
                })
                print(f"[✅ Admin Notified] Admin ID: {admin.id} - {admin.email} for Car: {car_info}")
            
                
                
            
            
    



# GUEST with car detail model
class Guest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("assigned", "Assigned"),
        ("in_inspection", "In Inspection"),
        ("await_approval", " Awating Approval"),
        ("rejected", "Rejected"),
        ("bidding", "In Bidding"),
        ("expired", "Expired"),
        ("in_inventory" , "In Inventory"),
        ("sold", "Sold"),
    ]   
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=30)
    email = models.CharField(max_length=100)
    inspector = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inspector_in_guest",
    ) 
    winner_dealer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dealer_inventory",
    )
    is_sold = models.BooleanField(default=False)
    car_name = models.CharField(max_length=100)
    car_variant = models.CharField(max_length=100, null=True,blank=True)
    company = models.CharField(max_length=100)
    year = models.CharField(max_length=20)
    engine_size = models.CharField(max_length=20)
    milage = models.CharField(max_length=100)
    option_type = models.CharField(max_length=50, choices=OPTION_CHOICES)
    paint_condition = models.CharField(max_length=100, choices=PAINT_CHOICES)
    specs = models.CharField(max_length=100, choices=SPECIFICATON_OPTIONS)
    photos = models.JSONField(null=True, blank=True)
    inspection_date = models.DateField(null=True,blank=True)
    inspection_time = models.CharField(max_length=20 , null=True , blank=True) ##change 15/5/2025
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")
    is_inspected = models.BooleanField(default=False)
    added_by = models.CharField(max_length=50, blank=True, null=True)
    is_manual = models.BooleanField(default=False)
    is_booked = models.BooleanField(default=False)
    bidding_start_time = models.DateTimeField(null=True, blank=True)
    bidding_end_time = models.DateTimeField(null=True, blank=True)
    demand = models.DecimalField(max_digits=60, decimal_places=2, null=True,blank=True)
    min_bid_amount  = models.DecimalField(max_digits=60,decimal_places=2,null=True,blank=True)


    # def start_bidding(self):
    #     self.bidding_start_time = timezone.now()
    #     self.bidding_end_time = self.bidding_start_time + timedelta(days=10)
    #     self.save()

    def is_bidding_active(self):
        now_time = timezone.now()
        return (
            self.bidding_start_time
            and self.bidding_end_time
            and self.bidding_start_time <= now_time <= self.bidding_end_time
        )

    def save(self, *args, **kwargs):
        now_time = timezone.now()
        was_expired = self.status == "expired"
        

        # Mark sold
        if self.status == "sold":
            self.is_sold = True

        # Auto-expire if bidding time passed
        if (
            self.status == "bidding"
            and self.bidding_end_time
            and now_time > self.bidding_end_time
            and not self.is_sold
        ):
            self.status = "expired"

        super().save(*args, **kwargs)
        
        if self.status == "expired" and not was_expired:
            car_info = f"{self.company} {self.car_name} {self.car_variant}"
            
            # ====notify Owner=====
            # if self.user:
            #     message = f"Your {car_info} has been expired"
                
            #     Notification.objects.create(
            #     recipient=self.user,
            #     message=message,
            #     saler_car=self,
            #     category="seller_car_expired",
            # )
            # send_notification(
            #     title="Car Expired",
            #     body=message,
            #     user=self.user,
            # )
            
            # geting user model
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # ===Notify dealers===
            dealers = User.objects.filter(role="dealer")
            
            # sample message for dealer
            message = f"The bidding period of {car_info} has been ended."
            
            for dealer in dealers:
                Notification.objects.create(
                    recipient=dealer,
                    message = message,
                    saler_car = self,
                    category="dealer_car_expied"
                )
            # ===push notification Dealer ===
                send_notification(title="Car Expired" , body=message , user=dealer,more_detail={
                    "car_type": "seller",
                    "car_id": str(self.id),
                    "car_name": self.car_name,
                    "tab": "expire",
                })
            
            # ===notifiy Admin===
            
            # --get all admins from model--
            admins = User.objects.filter(role="admin")
            
            # ---sample message--
            message = f"{car_info} has been expired. No winning Bid"
            
            for admin in admins:
                Notification.objects.create(
                    recipient = admin,
                    message = message,
                    saler_car= self,
                    category = "admin_car_expired" 
                )
                send_notification(title="Car Expired", body=message, user=admin,more_detail={
                    "car_type": "seller",
                    "car_id": str(self.id),
                    "car_name": self.car_name,
                    "tab": "expire",
                })
    
    
    
    

# inspector availability model
class Availability(models.Model):
    inspector = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "inspector"},
        related_name="inspector",
    )
    date = models.DateField()
    time_slots = models.JSONField(default=list)

    def __str__(self):
        return f"{self.inspector.username} - {self.date}"


# saler select the time for inspection
class SelectedSlot(models.Model):
    saler_car = models.ForeignKey(
        saler_car_details,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="selected_slots",
    )
    inspector = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "inspector"},
    )
    unreg_guest = models.ForeignKey(Guest,on_delete=models.SET_NULL, null=True,blank=True)
    date = models.DateField()
    time_slot = models.TimeField()
    BOOKED_BY_CHOICES = [
        ("seler", "Seller"),
        ("inspector", "Inspector"),
        ("guest", "Guest"),
    ]
    booked_by = models.CharField(
        max_length=10, choices=BOOKED_BY_CHOICES, default="seller"
    )


class InspectionReport(models.Model):
    inspector = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={"role": "inspector"},
    )
    saler_car = models.ForeignKey(
        saler_car_details, on_delete=models.CASCADE,null=True,blank=True, related_name="inspection_reports"
    )
    guest_car = models.ForeignKey(Guest , on_delete=models.CASCADE, null=True, blank=True, related_name="guest_inspection_reports")
    json_obj = models.JSONField(null=True, blank=True)
    image_urls = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)


    def approve_inspection(self):
        if self.saler_car and self.saler_car.status == "await_approval":
            self.saler_car.status = "bidding"
            self.saler_car.save()

            self.is_accepted = True
            self.is_rejected = False
            self.save()

            Notification.objects.create(
                recipient=self.saler_car.user,
                message=f"Your car {self.saler_car.car_name} has been Approved for bidding",
                saler_car=self.saler_car,
                category="inspection_approved",
            )

        elif self.guest_car and self.guest_car.status == "await_approval":
            self.guest_car.status = "bidding"
            self.guest_car.is_inspected = True
            self.guest_car.save()

            self.is_accepted = True
            self.is_rejected = False
            self.save()

    def reject_inspection(self):
        if self.saler_car and self.saler_car.status == "await_approval":
            self.saler_car.status = "rejected"
            self.saler_car.save()

            self.is_rejected = True
            self.is_accepted = False
            self.save()

            Notification.objects.create(
                recipient=self.saler_car.user,
                message=f"Your car {self.saler_car.car_name} has been rejected for bidding",
                saler_car=self.saler_car,
                category="inspection_rejected",
            )

        elif self.guest_car and self.guest_car.status == "await_approval":
            self.guest_car.status = "rejected"
            self.guest_car.save()

            self.is_rejected = True
            self.is_accepted = False
            self.save()

    def __str__(self):
        return f"Inspection Report for {self.saler_car.car_name} by {self.inspector.username} on {self.created_at}"


# Bidding model
class Bidding(models.Model):
    dealer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "dealer"},
        related_name="bids",
    )
    saler_car = models.ForeignKey(
        saler_car_details, on_delete=models.CASCADE, related_name="bids",null=True,blank=True
    )
    guest_car = models.ForeignKey(Guest , null=True , blank=True, on_delete=models.CASCADE, related_name="guest_car_bid")
    bid_amount = models.DecimalField(max_digits=65, decimal_places=2)
    bid_date = models.DateField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
            ("expired", "Expired"),
        ],
        default="pending",
    )

    def __str__(self):
        return f"Dealer :{self.dealer.username}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # For seller cars
        if self.saler_car:
            if (
                not self.saler_car.min_bid_amount
                or self.bid_amount > self.saler_car.min_bid_amount
            ):
                self.saler_car.min_bid_amount = self.bid_amount
                self.saler_car.save(update_fields=["min_bid_amount"])

        # For guest cars
        if self.guest_car:
            if (
                not self.guest_car.min_bid_amount
                or self.bid_amount > self.guest_car.min_bid_amount
            ):
                self.guest_car.min_bid_amount = self.bid_amount
                self.guest_car.save(update_fields=["min_bid_amount"])




# notification model for saler car posting
class Notification(models.Model):
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifecation"
    )
    bid = models.ForeignKey(
        Bidding,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="bid_acception",
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    saler_car = models.ForeignKey(
        saler_car_details,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )
    guest_car = models.ForeignKey( 
        Guest,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )
    category = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return f"Notifecation for {self.recipient.username} : {self.message[:20]}"


# notification when inspection report posted by inspector
class InspectionReportNotification(models.Model):
    recepient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="inspection_notification"
    )
    report = models.ForeignKey(
        InspectionReport, on_delete=models.CASCADE, related_name="notification"
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


# (Inspector assign slot to seller --manual entry)
class AssignSlot(models.Model):
    inspector = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "inspector"},
        related_name="assigning_slots",
    )
    car = models.ForeignKey(
        saler_car_details, on_delete=models.CASCADE, null=True,blank=True, related_name="assigned_slots"
    )
    guest_car = models.ForeignKey(Guest , on_delete=models.CASCADE, null=True,blank=True, related_name="assigned_slot_to_guest")
    inspection_date = models.DateField(null=True,blank=True)
    inspection_time = models.CharField(max_length=20 , null=True , blank=True) ##change 15/5/2025
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_by = models.CharField(max_length=50, default="inspector")
    

    def __str__(self):
        return f"Slot for {self.car.car_name} ({self.car.model}) on {self.date} at {self.time_slot}"


# for inspection saler name and number
class AdditionalDetails(models.Model):
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.name}"


# device id model
class DeviceToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    device_id = models.CharField(max_length=300)
    token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)



class DeviceDetail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  
    role = models.CharField(max_length=20 , null=True , blank=True)
    device_token = models.CharField(max_length=255, null=True , blank=True)
  
  