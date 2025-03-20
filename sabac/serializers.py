import base64
import json
from time import timezone
import uuid
from django.core.files.base import ContentFile
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from .models import User , saler_car_details ,CarPhoto,Availability,SelectedSlot,InspectionReport,Bidding,Notification,AssignSlot,AdditionalDetails,Guest
from drf_extra_fields.fields import Base64ImageField


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'role',
            'phone_number',
            'adress'
        ]
        extra_kwargs = {
            'password' : {'write_only' : True}
        }
    def create(self, validated_data):
        # Hash the password and create the user
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password) 
        user.save()
        return user
    
        
# saler car photo
class CarPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarPhoto
        fields = ['car', 'photo_base64']

    # Optional: To validate base64 string
    def validate_photo_base64(self, value):
        if not value.startswith("data:image"):
            raise serializers.ValidationError("Invalid image base64 string.")
        return value
        
    
    
    
class SalerCarDetailsSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True, required=False)
    is_sold = serializers.BooleanField(read_only=True)
    added_by = serializers.CharField(required=False, allow_blank=True)  
    inspector = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role="inspector"), allow_null=True, required=False)
    
    guest = serializers.SerializerMethodField()  # ✅ Fetch guest details

    class Meta:
        model = saler_car_details
        fields = [
            'saler_car_id',
            'user',
            'guest',  # ✅ Added guest details
            'car_name',
            'company',
            'color',
            'condition',
            'model',
            'demand',
            'city',
            'is_sold',
            'milage',
            'description',
            'type',
            'fuel_type',
            'registered_in',
            'assembly',
            "engine_capacity",
            'photos',
            'phone_number',
            'secondary_number',
            'status',
            'created_at',
            'updated_at',
            'is_inspected',
            'added_by',
            'inspector'
        ]
        read_only_fields = ["status", "is_sold"]

    def get_guest(self, obj):
        """Retrieve guest details"""
        if obj.guest:
            return {
                "name": obj.guest.name,
                "number": obj.guest.number,
                "email": obj.guest.email
            }
        return None

        # extra_kwargs = {'user': {'required': False, 'allow_null': True}}

        
# inspector Availability 
class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = ['date', 'time_slot']  
        
# slot selection
class SelectedSlotSerializer(serializers.ModelSerializer):
    
    saler_car_details = serializers.SerializerMethodField()
    saler_detail = serializers.SerializerMethodField()
    # inspector_details = serializers.SerializerMethodField()
    
    class Meta:
        model = SelectedSlot
        fields = ['id' , 'saler_car_details' , 'saler_detail' , 'date', 'time_slot']
        
        
    def get_saler_car_details(self , obj):
        return{
            'car_name' : obj.saler_car.car_name,
            'company' : obj.saler_car.company,
            'color' : obj.saler_car.color
        }
        
    
    def get_saler_detail(self, obj):
        saler = obj.saler_car.user  
        return {
            'saler_name': saler.username,
            'email': saler.email
        }
        
class InspectionReportSerializer(serializers.ModelSerializer):
    user = UserSerializer(source="saler_car.user", read_only=True)

    car_photos = serializers.ListField(child=serializers.CharField(), required=False)  # Accepts base64 strings

    class Meta:
        model = InspectionReport
        fields = [
            'id', 'inspector', 'saler_car', 'car_name', 'company', 'color', 'condition', 'model', 
            'fuel_type', 'registry_number', 'year', 'engine_capacity', 'mileage', 'chassis_number', 
            'engine_type', 'transmission_type', 'engine_condition', 'body_condition', 'clutch_condition', 
            'steering_condition', 'suspension_condition', 'brakes_condition', 'ac_condition', 
            'electrical_condition', 'estimated_value', 'saler_demand','car_photos','overall_score','inspection_date','user'
        ]



# Bidding model serializer
class BiddingSerializer(serializers.ModelSerializer):
    dealer_name = serializers.CharField(source='dealer.username', read_only = True)
    car_name = serializers.CharField(source = 'saler_car.car_name', read_only=True)
    car_id = serializers.IntegerField(source='saler_car.id', read_only=True)
    owner_details = serializers.SerializerMethodField()
    is_sold = serializers.BooleanField(source = 'saler_car.is_sold', read_only=True)
    
    class Meta:
        model = Bidding
        fields = ['dealer' , 'saler_car' , 'bid_amount','is_accepted', 'dealer_name', 'car_name','car_id','is_sold', 'owner_details']
        
    def get_owner_details(self , obj):
        owner = obj.saler_car.user
        return{
            'owner_name' : owner.username,
            'owner_email' : owner.email
        }
        
        
class NotificationSerializer(serializers.ModelSerializer):
    bid_id = serializers.PrimaryKeyRelatedField(source='bid.id', read_only=True)

    # recepient_username = serializers.CharField(source= 'recepient_username',read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'recipient','message','created_at','is_read', 'category' , 'bid_id']
        

        
        
class Base64ImageField(serializers.ImageField):
    """Custom field to handle base64 image data"""

    def to_internal_value(self, data):
        """Convert base64 string to an image file"""
        if isinstance(data, str) and data.startswith("data:image"):
            # Decode the base64 string
            format, imgstr = data.split(";base64,")  # Format: data:image/png;base64,....
            ext = format.split("/")[-1]  # Extract extension (png, jpg, etc.)

            # Generate a unique filename
            file_name = f"{uuid.uuid4()}.{ext}"

            # Convert base64 string to Django ContentFile
            data = ContentFile(base64.b64decode(imgstr), name=file_name) # type: ignore

        return super().to_internal_value(data)
    


class AssignedSlotSerializer(serializers.ModelSerializer):
    inspector = serializers.ReadOnlyField(source="inspector.username")
    inspector_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="inspector"), write_only=True
    )
    car_id = serializers.IntegerField(write_only=True)  # ✅ Accept integer car_id
    car = SalerCarDetailsSerializer(read_only=True)  # ✅ Keep car read-only

    class Meta:
        model = AssignSlot
        fields = ["id", "inspector", "inspector_id", "car_id", "car", "date", "time_slot", "assigned_by"]
        read_only_fields = ["inspector", "assigned_by", "car"]  # ✅ `car` should be read-only

    def create(self, validated_data):
        """Create AssignSlot and add to SelectedSlot"""
        inspector = validated_data.pop("inspector_id")
        car_id = validated_data.pop("car_id")  # ✅ Extract car_id

        try:
            car = saler_car_details.objects.get(saler_car_id=car_id)  # ✅ Fetch car object
        except saler_car_details.DoesNotExist:
            raise serializers.ValidationError({"car_id": "Invalid Car ID"})

        assigned_slot = AssignSlot.objects.create(
            inspector=inspector,
            assigned_by="inspector",  # ✅ Explicitly setting the field
            car=car,  # ✅ Assign the fetched car object
            **validated_data
        )

        # ✅ Also save in `SelectedSlot`
        SelectedSlot.objects.create(
            inspector=inspector,
            saler_car=car,  # ✅ Assign the car object, not an ID
            date=assigned_slot.date,
            time_slot=assigned_slot.time_slot
        )

        return assigned_slot



class AdditionalDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalDetails
        
        fields = [
            "name" , "number"
        ]
class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        
        fields = [
            "name" , "number" , "email"
        ]

      
        


        

