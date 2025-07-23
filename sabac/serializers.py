import base64
import uuid
from datetime import datetime

from django.core.files.base import ContentFile
from rest_framework import serializers

from .models import (
    AdditionalDetails,
    AssignSlot,
    Availability,
    Bidding,
    DeviceToken,
    Guest,
    InspectionReport,
    Notification,
    SelectedSlot,
    User,
    saler_car_details,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "plain_password",
            "role",
            "phone_number",
            "adress",
            "image",
        ]
        extra_kwargs = {
            "plain_password": {"read_only": True},
        }

    def create(self, validated_data):
        # password hashing
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.plain_password=password
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.get("password", None)
        if password:
            instance.set_password(password)
            instance.plain_password = password  # store plain password
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


    #GUEST & CAR DETAIL SERIALIZER    
class GuestSerializer(serializers.ModelSerializer):
    inspector_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="inspector"),
        source="inspector",
        write_only=True,
        required=False,
        allow_null=True
    )
    inspector = serializers.SerializerMethodField()
    photos = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        allow_null=True
    )
    class Meta:
        model = Guest
        fields = [
            "id",
            "name",
            "number",
            "email",
            "inspector_id",
            "inspector",
            "winner_dealer", 
            "car_name",
            "car_variant",
            "company",
            "year",
            "engine_size",
            "milage",
            "option_type",
            "paint_condition",
            "specs",
            "photos",
            "inspection_date",
            "inspection_time",
            "status",
            "is_inspected",
            "is_sold",
            "is_manual",
            "is_booked",
            "added_by",
            "bidding_start_time",
            "bidding_end_time",
            "demand",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "is_sold",
            "is_inspected",
            "created_at",
            "updated_at",
            "bidding_start_time",
            "bidding_end_time",
            "inspector",
        ]

    def get_inspector(self, obj):
        if obj.inspector:
            return {
                "id": obj.inspector.id,
                "name": obj.inspector.get_full_name() or obj.inspector.username,
                "email": obj.inspector.email
            }
        return None

    def validate_inspection_time(self, value):
        if value:
            try:
                datetime.strptime(value.strip(), "%I:%M %p")  # 12-hour format
            except ValueError:
                raise serializers.ValidationError("Time must be in 12-hour format, e.g., '02:30 PM'.")
        return value
        
  

# Device token serializer
class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = "__all__"



# seller car detail serializer
class SalerCarDetailsSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), allow_null=True, required=False
    )
    is_sold = serializers.BooleanField(read_only=True)
    added_by = serializers.CharField(required=False, allow_blank=True)
    inspector = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="inspector"), allow_null=True, required=False
    )
    seller = UserSerializer(source="user", read_only=True)
    photos = serializers.ListField(
        child=serializers.URLField(), allow_null=True, required=False
    )
    inspection_time = serializers.CharField(required=False, allow_null=True)
    inspection_date = serializers.DateField(required=False, allow_null=True)  


    class Meta:
        model = saler_car_details
        fields = [
            "saler_car_id",
            "user",
            "car_name",
            "car_variant",
            "company",
            "year",
            "engine_size",
            "milage",
            "option_type",
            "paint_condition",
            "specs",
            "inspection_date",
            "inspection_time",
            "created_at",
            "updated_at",
            "status",
            "is_inspected",
            "bidding_start_time",
            "bidding_end_time",
            "primary_phone_number",
            "secondary_phone_number",
            "demand",
            "added_by",
            "is_booked",
            "is_manual",
            "is_sold",
            "photos",
            "inspector",
            "seller",
        ]
        read_only_fields = ["status", "is_sold"]
    def validate_inspection_time(self, value):
        if value:
            try:
                # Try parsing as 12-hour format
                datetime.strptime(value.strip(), "%I:%M %p")
            except ValueError:
                raise serializers.ValidationError("Time must be in 12-hour format (e.g., 02:30 PM)")
        return value


# inspector Availability
class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = ["date", "time_slot"]




# slot selection
class SelectedSlotSerializer(serializers.ModelSerializer):
    saler_car_details = serializers.SerializerMethodField()
    saler_detail = serializers.SerializerMethodField()

    class Meta:
        model = SelectedSlot
        fields = ["id", "saler_car_details", "saler_detail", "date", "time_slot","unreg_guest"]

    def get_saler_car_details(self, obj):
        return {
            "car_name": obj.saler_car.car_name,
            "company": obj.saler_car.company,
            "color": obj.saler_car.color,
        }

    def get_saler_detail(self, obj):
        saler = obj.saler_car.user
        return {"saler_name": saler.username, "email": saler.email}



# INSPECTION REPORT SERIALIZER
class InspectionReportSerializer(serializers.ModelSerializer):
    image_urls = serializers.ListField(
        child=serializers.URLField(), required=False, allow_null=True
    )
    
    saler_car = SalerCarDetailsSerializer(read_only=True)
    guest_car = GuestSerializer(read_only=True)
    
    class Meta:
        model = InspectionReport
        fields = "__all__"


# Bidding model serializer
class BiddingSerializer(serializers.ModelSerializer):
    dealer_name = serializers.CharField(source="dealer.username", read_only=True)
    car_name = serializers.CharField(source="saler_car.car_name", read_only=True)
    car_id = serializers.IntegerField(source="saler_car.id", read_only=True)
    is_sold = serializers.BooleanField(source="saler_car.is_sold", read_only=True)
    saler_car = SalerCarDetailsSerializer(read_only=True)

    class Meta:
        model = Bidding
        fields = [
            "id",
            "bid_amount",
            "is_accepted",
            "dealer_name",
            "car_name",
            "car_id",
            "is_sold",
            "created_at",
            "dealer",
            "saler_car",
            "guest_car"
        ]


# NOTIFICATION SERIALIZER
class NotificationSerializer(serializers.ModelSerializer):
    bid = BiddingSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "message",
            "created_at",
            "is_read",
            "category",
            "bid",
            "recipient",
            "guest_car"
        ]





class Base64ImageField(serializers.ImageField):
    """Custom field to handle base64 image data"""

    def to_internal_value(self, data):
        """Convert base64 string to an image file"""
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            file_name = f"{uuid.uuid4()}.{ext}"

            data = ContentFile(base64.b64decode(imgstr), name=file_name)

        return super().to_internal_value(data)


# ASSINGNNG SLOT 
class AssignedSlotSerializer(serializers.ModelSerializer):
    inspector = serializers.ReadOnlyField(source="inspector.username")
    inspector_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="inspector"), write_only=True
    )
    car_id = serializers.IntegerField(write_only=True)
    car = SalerCarDetailsSerializer(read_only=True)
    guest = GuestSerializer(source="guest_car", read_only=True)


    class Meta:
        model = AssignSlot
        fields = [
            "id",
            "inspector",
            "inspector_id",
            "car_id",
            "car",
            "guest_car",
            "guest",
            "inspection_date",
            "inspection_time",
            "assigned_by",
        ]
        read_only_fields = ["inspector", "assigned_by", "car","guest"]

    def create(self, validated_data):
        inspector = validated_data.pop("inspector_id")
        car_id = validated_data.pop("car_id") 

        try:
            car = saler_car_details.objects.get(
                saler_car_id=car_id
            ) 
        except saler_car_details.DoesNotExist:
            raise serializers.ValidationError({"car_id": "Invalid Car ID"})

        assigned_slot = AssignSlot.objects.create(
            inspector=inspector, assigned_by="inspector", car=car, **validated_data
        )
        return assigned_slot


class AdditionalDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalDetails

        fields = ["name", "number"]


# USED IN VIEW TO CAR COUNTS
class CarListingSerializer(serializers.ModelSerializer):
    total_cars_today = serializers.IntegerField()
    total_cars_this_week = serializers.IntegerField()
    total_cars_this_month = serializers.IntegerField()
