import base64
import uuid
from django.core.files.base import ContentFile
from rest_framework import serializers
from .models import User,  saler_car_details, Availability, SelectedSlot, InspectionReport, Bidding, Notification, AssignSlot, AdditionalDetails, Guest, DeviceToken


class UserSerializer(serializers.ModelSerializer):
    image = serializers.CharField(required=False, allow_blank=True)

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
            'adress',
            'image'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_image(self, value):
        """Ensure the image is a valid Base64 string."""
        if value:
            try:
                # Decode Base64 string
                decoded_data = base64.b64decode(value)

                # Ensure it's a valid image by checking file signature (optional)
                if not decoded_data.startswith(b'\xFF\xD8') and not decoded_data.startswith(b'\x89PNG'):
                    raise serializers.ValidationError(
                        "Invalid image format. Only JPEG and PNG are supported.")

            except Exception:
                raise serializers.ValidationError(
                    "Invalid Base64-encoded image.")
        return value

    def create(self, validated_data):
        # Hash the password and create the user
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# Device token serializer
class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = "__all__"


# saler car photo


class SalerCarDetailsSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), allow_null=True, required=False)
    is_sold = serializers.BooleanField(read_only=True)
    added_by = serializers.CharField(required=False, allow_blank=True)
    inspector = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="inspector"), allow_null=True, required=False)
    seller = UserSerializer(source="user", read_only=True)
    guest = serializers.SerializerMethodField()
    photos = serializers.ListField(
        child=serializers.URLField(),
        allow_null=True,
        required=False
    )

    class Meta:
        model = saler_car_details
        fields = [
            'saler_car_id',
            'user',
            'guest',
            'car_name',
            'company',
            'year',
            'engine_size',
            'milage',
            'option_type',
            'paint_condition',
            'specs',
            'inspection_date',
            'inspection_time',
            'created_at',
            'updated_at',
            'status',
            'is_inspected',
            'bidding_start_time',
            'bidding_end_time',
            'primary_phone_number',
            'secondary_phone_number',
            'added_by',
            'is_booked',
            'is_manual',
            'is_sold',
            'photos',
            'inspector',
            'seller',


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


# class SalerCarDetailsSerializer(serializers.ModelSerializer):
#     user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True, required=False)
#     is_sold = serializers.BooleanField(read_only=True)
#     added_by = serializers.CharField(required=False, allow_blank=True)
#     inspector = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role="inspector"), allow_null=True, required=False)
#     seller = UserSerializer(source="user",read_only=True)
#     guest = serializers.SerializerMethodField()  # ✅ Fetch guest details

#     class Meta:
#         model = saler_car_details
#         fields = [
#             'saler_car_id',
#             'user',
#             'guest',
#             'car_name',
#             'company',
#             'color',
#             'condition',
#             'model',
#             'demand',
#             'city',
#             'is_sold',
#             'milage',
#             'description',
#             'type',
#             'fuel_type',
#             'registered_in',
#             'assembly',
#             "engine_capacity",
#             'photos',
#             'status',
#             'created_at',
#             'updated_at',
#             'is_inspected',
#             'added_by',
#             'inspector',
#             'is_manual',
#             'seller',
#             'is_booked'
#         ]
#         read_only_fields = ["status", "is_sold"]


#     def get_guest(self, obj):
#         """Retrieve guest details"""
#         if obj.guest:
#             return {
#                 "name": obj.guest.name,
#                 "number": obj.guest.number,
#                 "email": obj.guest.email
#             }
#         return None

#         # extra_kwargs = {'user': {'required': False, 'allow_null': True}}


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
        fields = ['id', 'saler_car_details',
                  'saler_detail', 'date', 'time_slot']

    def get_saler_car_details(self, obj):
        return {
            'car_name': obj.saler_car.car_name,
            'company': obj.saler_car.company,
            'color': obj.saler_car.color
        }

    def get_saler_detail(self, obj):
        saler = obj.saler_car.user
        return {
            'saler_name': saler.username,
            'email': saler.email
        }


# class InspectionReportSerializer(serializers.ModelSerializer):
#     user = UserSerializer(source="saler_car.user", read_only=True)
#     # car_photos = serializers.ListField(child=serializers.CharField(), required=False)

#     class Meta:
#         model = InspectionReport
#         fields = [
#             'id', 'inspector', 'saler_car', 'car_name', 'company', 'color', 'condition', 'model',
#             'fuel_type', 'year', 'engine_capacity', 'mileage', 'variant', 'registered_in',
#             'engine_type', 'transmission_type', 'chasis_number', 'engine_number',
#             'engine_condition', 'body_condition', 'clutch_condition', 'steering_condition',
#             'suspension_condition', 'brakes_condition', 'ac_condition', 'tyres_condition',
#             'electrical_condition', 'estimated_value', 'saler_demand', 'car_photos',
#             'overall_score', 'inspection_date', 'user', 'is_accepted', 'is_rejected',

#             'front_right_fender', 'front_left_fender', 'bonnet_paint_condition', 'bonnet_seals_condition',
#             'front_drive_door_paint_conditions', 'front_drive_door_seals_conditions',
#             'front_pessenger_door_paint_conditions', 'front_pessenger_door_seals_conditions',
#             'rear_right_door_paint_condtion', 'rear_right_door_seals_condtion',
#             'rear_left_door_paint_condtion', 'rear_left_door_seals_condtion',
#             'rear_right_fender', 'rear_left_fender', 'outer_body_rust_marks','bonnet_photos','front_driver_photos','front_pessenger_door_photos','rear_right_door_photos','rear_left_door_photos','outer_body_rust_marks_photos','radiator_core_support_photos','right_strut_tower_apron_photos','left_strut_tower_apron_photos','right_front_rail_photos','left_front_rail_photos','cowl_panel_fire_wall_photos','right_pilar_front_photos','right_pilar_back_photos','left_pilar_front_photos','left_pilar_back_photos','right_front_side_panel_photos','right_rare_side_panel_photos','left_front_side_panel_photos','left_rare_side_panel_photos','body_frame_rust_marks_photos',

#             'radiator_core_support', 'right_strut_tower_apron', 'left_strut_tower_apron',
#             'right_front_rail', 'left_front_rail', 'cowl_panel_fire_wall',
#             'right_pilar_front', 'right_pilar_back', 'left_pilar_front', 'left_pilar_back',
#             'right_front_side_panel', 'right_rare_side_panel', 'left_front_side_panel', 'left_rare_side_panel',
#             'body_frame_rust_marks',

#             'engine_starts_properly', 'engine_health', 'engine_noise', 'gear_shifting', 'turning',
#             'suspension_check', 'exhaust',


#             'cruise_control', 'horn', 'cameras', 'sensors', 'warning_lights',

#             'front_left_door', 'rare_right_door', 'rare_left_door',
#             'steering_wheel', 'dashboard', 'front_driver_seat',
#             'front_pessrnger_seat', 'rare_seats', 'roof', 'boot_floor',

#             'spair_tyre', 'tools',

#             'electric_system', 'audio_system', 'wheels_and_brakes', 'oil_leak',
#             'water_leak', 'gear_oil_leak', 'steering_oil_leak', 'brake_oil_leak',
#             'vibration', 'hybrid', 'shocks', 'battery', 'mirrors_and_glass',
#             'lights', 'speedometer_working', 'service_history'
#         ]

class InspectionReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionReport
        fields = '__all__'

# Bidding model serializer


class BiddingSerializer(serializers.ModelSerializer):
    dealer_name = serializers.CharField(
        source='dealer.username', read_only=True)
    car_name = serializers.CharField(
        source='saler_car.car_name', read_only=True)
    car_id = serializers.IntegerField(source='saler_car.id', read_only=True)
    owner_details = serializers.SerializerMethodField()
    is_sold = serializers.BooleanField(
        source='saler_car.is_sold', read_only=True)

    class Meta:
        model = Bidding
        fields = ['dealer', 'saler_car', 'bid_amount', 'is_accepted',
                  'dealer_name', 'car_name', 'car_id', 'is_sold', 'owner_details', 'created_at']

    def get_owner_details(self, obj):
        owner = obj.saler_car.user
        return {
            'owner_name': owner.username,
            'owner_email': owner.email
        }


class NotificationSerializer(serializers.ModelSerializer):
    bid_id = serializers.PrimaryKeyRelatedField(
        source='bid.id', read_only=True)

    # recepient_username = serializers.CharField(source= 'recepient_username',read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'recipient', 'message',
                  'created_at', 'is_read', 'category', 'bid_id']


class Base64ImageField(serializers.ImageField):
    """Custom field to handle base64 image data"""

    def to_internal_value(self, data):
        """Convert base64 string to an image file"""
        if isinstance(data, str) and data.startswith("data:image"):
            # Decode the base64 string
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            file_name = f"{uuid.uuid4()}.{ext}"

            data = ContentFile(base64.b64decode(imgstr), name=file_name)

        return super().to_internal_value(data)


class AssignedSlotSerializer(serializers.ModelSerializer):
    inspector = serializers.ReadOnlyField(source="inspector.username")
    inspector_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="inspector"), write_only=True
    )
    car_id = serializers.IntegerField(write_only=True)
    car = SalerCarDetailsSerializer(read_only=True)

    class Meta:
        model = AssignSlot
        fields = ["id", "inspector", "inspector_id", "car_id",
                  "car", "date", "time_slot", "assigned_by"]
        read_only_fields = ["inspector", "assigned_by", "car"]

    def create(self, validated_data):
        """Create AssignSlot WITHOUT adding to SelectedSlot"""
        inspector = validated_data.pop("inspector_id")
        car_id = validated_data.pop("car_id")  # ✅ Extract car_id

        try:
            car = saler_car_details.objects.get(
                saler_car_id=car_id)  # ✅ Fetch car object
        except saler_car_details.DoesNotExist:
            raise serializers.ValidationError({"car_id": "Invalid Car ID"})

        # ✅ Only save in AssignSlot, DO NOT save in SelectedSlot
        assigned_slot = AssignSlot.objects.create(
            inspector=inspector,
            assigned_by="inspector",
            car=car,
            **validated_data
        )

        return assigned_slot


class AdditionalDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalDetails

        fields = [
            "name", "number"
        ]


class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest

        fields = [
            "name", "number", "email"
        ]


class CarListingSerializer(serializers.ModelSerializer):
    total_cars_today = serializers.IntegerField()
    total_cars_this_week = serializers.IntegerField()
    total_cars_this_month = serializers.IntegerField()
