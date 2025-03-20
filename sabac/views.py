import base64
import json
from time import timezone
from venv import logger
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view , permission_classes,authentication_classes
from .serializers import UserSerializer,SalerCarDetailsSerializer ,CarPhotoSerializer,AvailabilitySerializer,SelectedSlotSerializer,InspectionReportSerializer,BiddingSerializer,NotificationSerializer,AssignedSlotSerializer,AdditionalDetailSerializer,GuestSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated , AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .models import User , saler_car_details ,CarPhoto, Availability,SelectedSlot,InspectionReport,Bidding,Notification,InspectionReportNotification,AssignSlot, AdditionalDetails,Guest
from rest_framework import status
from datetime import datetime, timedelta
from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.db.models import F
import logging
from django.db.models import Max

logger = logging.getLogger(__name__)



class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        try:
            # Extract username or email from the request
            username_or_email = request.data.get('username_or_email')
            
            # Check if the input is an email
            if '@' in username_or_email:
                user = User.objects.get(email=username_or_email)
            else:
                user = User.objects.get(username=username_or_email)
            
            # Set the username in the request data for TokenObtainPairView
            request.data['username'] = user.username
            
            # Call the parent class's post method to generate tokens
            response = super().post(request, *args, **kwargs)
            tokens = response.data
            
            # Serialize the user data
            user_serializer = UserSerializer(user)
            
            # Prepare the response
            res = Response()
            res.data = {
                'success': True,
                'access_token': tokens['access'],
                'refresh_token': tokens['refresh'],
                'user': user_serializer.data,
            }
            
            # Set cookies for access and refresh tokens
            res.set_cookie(
                key='access_token',
                value=tokens['access'],
                httponly=True,
                secure=True,
                samesite='Lax',
                path='/'
            )
            res.set_cookie(
                key='refresh_token',
                value=tokens['refresh'],
                httponly=True,
                secure=True,
                samesite='Lax',
                path='/'
            )
            
            return res
        
        except ObjectDoesNotExist:
            return Response({'success': False, 'error': 'User not found'}, status=404)
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=400)

class CustomRefreshTokenView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            if not refresh_token:
                return Response({'refreshed': False, 'error': 'No refresh token found'})
            
            request.data['refresh'] = refresh_token
            response = super().post(request, *args, **kwargs)
            tokens = response.data
            
            res = Response()
            res.data = {'refreshed': True, 'access_token': tokens['access']}
            
            res.set_cookie(
                key='access_token',
                value=tokens['access'],
                httponly=True,
                secure=True,
                samesite='Lax',
                path='/'
            )
            return res
        except Exception as e:
            return Response({'refreshed': False, 'error': str(e)})
        
# for check authentecated
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def is_authentecated(request):
    return Response({'authentecation' : True})


# ADMIN REGISTER THE DEALER AND INSPECTOR
@api_view(['POST'])
@authentication_classes([]) # authentecation is disabled
@permission_classes([AllowAny])
def register(request):
    allowed_roles = ['dealer' , 'inspector', 'admin']
    
    role = request.data.get('role')
    
    if role not in allowed_roles:
        return ValidationError({'role' : f"invalid Role. Allowed Roles are: {','.join(allowed_roles)}"})
    
    serializer = UserSerializer(data = request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)


# ADMIN UPDATE THE SALER & INSPECTOR
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def edit_user(request):
    admin = request.user

    user_id = request.data.get('id') 
    if not user_id:
        return Response({"message": "User ID is required to edit a user."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user_to_edit = User.objects.get(id=user_id)


        if user_to_edit != admin and admin.role != 'admin':
            return Response({"message": "Only admins can edit other users."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        user_to_edit.username = data.get('username', user_to_edit.username)
        user_to_edit.first_name = data.get('first_name', user_to_edit.first_name)
        user_to_edit.last_name = data.get('last_name', user_to_edit.last_name)
        user_to_edit.email = data.get('email', user_to_edit.email)
        user_to_edit.phone_number = data.get('phone_number', user_to_edit.phone_number)

        if user_to_edit != admin:
            new_role = data.get('role')
            allowed_roles = ['dealer', 'inspector', 'admin']
            if new_role and new_role in allowed_roles:
                user_to_edit.role = new_role
            elif new_role:
                return Response({
                    "message": f"Invalid role. Allowed roles are: {', '.join(allowed_roles)}"
                }, status=status.HTTP_400_BAD_REQUEST)

        user_to_edit.save()

        return Response({
            "message": "User updated successfully.",
            "id": user_to_edit.id,
            "username": user_to_edit.username,
            "first_name": user_to_edit.first_name,
            "last_name": user_to_edit.last_name,
            "email": user_to_edit.email,
            "phone_number": user_to_edit.phone_number,
            "role": user_to_edit.role,
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"message": f"Error updating user: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    
    

# ADMIN DELETE THE PROFILE OF DEALER AND INSPECTOR
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request):
    admin = request.user
    
    if admin.role != 'admin':
        return Response({"message" : "only admin can delete"})
    
    user_id = request.data.get('id')
    if not user_id:
        return Response({"message" : "user Id is required to delete user"})
    
    try:
        user_to_delete = User.objects.get(id=user_id)
        
        user_to_delete.delete()
        
        return Response({"message" : f"user with ID {user_id} deleted successfully"},status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error" : str(e)},status=status.HTTP_400_BAD_REQUEST)
    




# SALER ADD CAR FOR SALE
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_car_details(request):
    try:
        user = request.user
        data = request.data.copy()
        data['user'] = user.id
        data['added_by'] = "seller"

        # Serialize and save car details
        serializer = SalerCarDetailsSerializer(data=data)
        if serializer.is_valid():
            car_details = serializer.save()

            # Log the added car details
            print(f"Car added: {car_details.car_name} ({car_details.model}) by {user.username}")

            # Fetch the saler's phone number if available
            saler_phone_number = getattr(user, 'phone_number', 'N/A')
            print("Saler's phone number:", saler_phone_number)

            # Fetch all inspectors
            inspectors = User.objects.filter(role='inspector')

            # Create notifications for each inspector
            for inspector in inspectors:
                notification = Notification.objects.create(
                    recipient=inspector,
                    message=(
                        f"A new car ({car_details.car_name}, {car_details.model}) "
                        f"has been added by {user.username} (Phone: {saler_phone_number})."
                    ),
                    category='saler_car_details',
                )
                print(f"Created Notification ID: {notification.id} for inspector: {inspector.username}")

            # Return the serialized car details
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Handle invalid serializer data
        print("Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        # Log and return a generic error response
        print(f"Error in add_car_details view: {str(e)}")
        return Response(
            {'success': False, 'message': 'An error occurred while adding car details'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
# guest add car detail
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def guest_add_car_details(request):
#     try:
#         data = request.data.copy()
#         data['added_by'] = "guest"  # Marking as guest entry

#         # Extract guest details
#         guest_name = data.get('guest_name', 'Unknown Guest')

#         # Serialize and save car details
#         serializer = SalerCarDetailsSerializer(data=data)
#         if serializer.is_valid():
#             car_details = serializer.save()
            
#             return Response({
#                 "message": "Car added successfully!",
#                 "car_id": car_details.saler_car_id 
#             }, status=status.HTTP_201_CREATED)

#             # Log the added car details
#             print(f"Car added: {car_details.car_name} ({car_details.model}) by Guest: {guest_name}")

#             # Return the serialized car details
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         # Handle invalid serializer data
#         print("Serializer errors:", serializer.errors)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['POST'])
# @permission_classes([AllowAny])
# def guest_add_car_details(request):
#     try:
#         data = request.data.copy()
#         data['added_by'] = "guest"  # Marking the car as added by a guest

#         # ✅ Ensure we set the guest field
#         guest_user = User.objects.filter(email=data.get("email")).first()  # Assuming guest is identified by email
#         if guest_user:
#             data["guest"] = guest_user.id  # Assigning the guest to the car
        
#         # Serialize and save car details
#         serializer = SalerCarDetailsSerializer(data=data)
#         if serializer.is_valid():
#             car_details = serializer.save()

#             return Response({
#                 "message": "Car added successfully!",
#                 "car_id": car_details.saler_car_id
#             }, status=status.HTTP_201_CREATED)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     except Exception as e:
#         print(f"Error in guest_add_car_details view: {str(e)}")
#         return Response(
#             {'success': False, 'message': 'An error occurred while adding car details'},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )

@api_view(['POST'])
@permission_classes([AllowAny])
def guest_add_car_details(request):
    try:
        data = request.data.copy()
        data['added_by'] = "guest"  # Marking the car as added by a guest

        # ✅ Get Guest ID from request
        guest_id = data.get("guest_id")
        if not guest_id:
            return Response({"error": "Guest ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Find Guest
        try:
            guest = Guest.objects.get(id=guest_id)
        except Guest.DoesNotExist:
            return Response({"error": "Invalid Guest ID."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Remove guest_id from data before serialization
        data.pop("guest_id", None)

        # ✅ Serialize and save car details with guest
        serializer = SalerCarDetailsSerializer(data=data)
        if serializer.is_valid():
            car_details = serializer.save(guest=guest)  # Assigning the guest to the car
            
            return Response({
                "message": "Car added successfully!",
                "car_id": car_details.saler_car_id
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print(f"Error in guest_add_car_details view: {str(e)}")
        return Response(
            {'success': False, 'message': 'An error occurred while adding car details'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


        




# ✅ Assign inspector to a car (Guest or Seller)
@api_view(['POST'])
@permission_classes([AllowAny])  # Allow anyone (Guests & Sellers)
def assign_inspector_to_car(request):
    try:
        print("Incoming request data:", request.data)  # Debugging log

        car_id = request.data.get('car_id')
        inspector_id = request.data.get('inspector_id')

        if not car_id or not inspector_id:
            return Response({"error": "Car ID and Inspector ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Validate inspector (role="inspector")
        try:
            inspector = User.objects.get(id=inspector_id, role="inspector")
        except User.DoesNotExist:
            return Response({"error": "Invalid inspector selected"}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Validate car (Guest or Seller's car)
        try:
            car = saler_car_details.objects.get(saler_car_id=car_id)
        except saler_car_details.DoesNotExist:
            return Response({"error": "Car not found"}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Assign inspector to the car
        car.inspector = inspector
        car.save()

        return Response({"message": "Inspector assigned successfully!"}, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Error in assign_inspector_to_car: {e}")  # Debugging
        return Response(
            {'success': False, 'message': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



# ✅ Assign inspector to a seller's car
@api_view(['POST'])
@permission_classes([AllowAny])
def assign_inspector_to_seller_car(request):
    try:
        print("Incoming request data:", request.data)  # Debugging log

        car_id = request.data.get('car_id')
        inspector_id = request.data.get('inspector_id')

        if not car_id or not inspector_id:
            return Response({"error": "Car ID and Inspector ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Validate inspector (role="inspector")
        try:
            inspector = User.objects.get(id=inspector_id, role="inspector")
        except User.DoesNotExist:
            return Response({"error": "Invalid inspector selected"}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Validate car (Must be a seller's car)
        try:
            car = saler_car_details.objects.get(saler_car_id=car_id, added_by="seller")
        except saler_car_details.DoesNotExist:
            return Response({"error": "Seller's car not found"}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Assign inspector to the seller's car
        car.inspector = inspector
        car.save()

        return Response({"message": "Inspector assigned to seller's car successfully!"}, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Error in assign_inspector_to_seller_car: {e}")  # Debugging
        return Response(
            {'success': False, 'message': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



        
# get list of cars to show to inspector
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_guest_car_details(request):
    try:
        inspector_id = request.GET.get('inspector_id')  # Get inspector ID from request

        if not inspector_id:
            return Response({"error": "Inspector ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Validate Inspector
        try:
            inspector = User.objects.get(id=inspector_id, role__iexact="Inspector")
        except User.DoesNotExist:
            return Response({"error": "Invalid inspector ID"}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Fetch only cars added by a "guest"
        assigned_cars = saler_car_details.objects.filter(
            inspector=inspector,
            status="pending",
            added_by="guest"  # Ensure only guest cars are fetched
        ).select_related('guest')

        # ✅ Serialize the data
        serializer = SalerCarDetailsSerializer(assigned_cars, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Error in get_guest_car_details: {e}")  # Debugging
        return Response(
            {'success': False, 'message': f'Error retrieving assigned cars: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


#GET THE CAR DETAILS OF SALER
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_car_details(request):
    user = request.user  # Get the authenticated user

    # Fetch all cars associated with the authenticated user
    cars = saler_car_details.objects.filter(user=user)
    if not cars.exists():
        return Response({"detail": "No car details found for this user."}, status=status.HTTP_404_NOT_FOUND)

    serializer = SalerCarDetailsSerializer(cars, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_list_of_car_for_inspection(request):
    try:
        all_cars = saler_car_details.objects.all()

        serializer = SalerCarDetailsSerializer(all_cars, many=True)

        total_cars = all_cars.count()
        
        today = now().date()
        
        cars_today = all_cars.filter(created_at__date=today).count()
        
        # Calculate progress of all cars
        all_cars_progress = 0
        if total_cars > 0:
            all_cars_progress = (cars_today / total_cars) * 100

        # Prepare the response data
        response_data = {
            "total_cars": total_cars,
            "cars_today": cars_today,
            "all_cars_progress": round(all_cars_progress, 2),  # Round to 2 decimal places
            "cars": serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Error in get_list_of_car_for_inspection: {str(e)}")
        return Response(
            {"error": "An error occurred while fetching the car list."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# get the last car details only
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_last_car_details(request):
    user = request.user

    last_car = saler_car_details.objects.filter(user=user).order_by('-saler_car_id').first()
    if not last_car:
        return Response({"detail": "No car details found for this user."}, status=status.HTTP_404_NOT_FOUND)

    serializer = SalerCarDetailsSerializer(last_car)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_inspectors(request):
    try:
        inspector = User.objects.filter(role = "inspector")
        serializer = UserSerializer(inspector,many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

 
 
 
 
        
# GETTING & POSTING THE PHOTOS OF SALER CAR
@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated]) 
def salerCarPhoto(request):
    if request.method == 'POST':
        data = request.data
        serializer = CarPhotoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'GET':
        car_id = request.query_params.get('car' , None)
        
        if car_id:
            car_photos = CarPhoto.objects.filter(car = car_id)
        else :
            car_photos = CarPhoto.objects.all()
        serializer = CarPhotoSerializer(car_photos , many=True)
        return Response(serializer.data , status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_availability(request):
    user = request.user

    # Ensure only Inspectors can add availability
    if user.role.lower() != 'inspector':
        return Response({'message': 'Only an inspector can add availability'}, status=403)

    data = request.data
    date_slots = data.get('dateSlots')  # Expecting a list of { date, slots }

    if not date_slots or not isinstance(date_slots, list):
        return Response({'message': 'A list of date and slot pairs is required'}, status=400)

    for entry in date_slots:
        date_str = entry.get('date')
        slots = entry.get('slots')

        if not date_str or not slots:
            return Response({'message': 'Each entry must have a valid date and slots'}, status=400)

        # Validate date format
        try:
            current_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({'message': 'Invalid date format. Use YYYY-MM-DD'}, status=400)

        # Restrict maximum slots per day
        if len(slots) > 24:
            return Response({'message': 'You cannot add more than 24 slots per day'}, status=400)

        # Validate and normalize time slots
        valid_slots = set()  # Using a set to ensure unique slots
        for slot in slots:
            try:
                if "AM" in slot.upper() or "PM" in slot.upper():
                    slot_time = datetime.strptime(slot, "%I:%M %p").time()  # Convert 12-hour format
                else:
                    slot_time = datetime.strptime(slot, "%H:%M").time()  # Convert 24-hour format

                valid_slots.add(slot_time.strftime("%H:%M"))  # Store in 24-hour format
            except ValueError:
                return Response({'message': f"Invalid time format: {slot}. Use HH:MM or 12-hour format (e.g., 2:30 PM)"}, status=400)

        # Retrieve existing availability
        availability, created = Availability.objects.get_or_create(
            inspector=user, date=current_date
        )

        # Append new slots without duplicates
        existing_slots = set(availability.time_slots) if availability.time_slots else set()
        updated_slots = list(existing_slots.union(valid_slots))  # Merge and ensure uniqueness

        # Update availability
        availability.time_slots = updated_slots
        availability.save()

    return Response({'message': 'Availability slots added successfully'}, status=201)






# GET ALL SLOTS
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_slot(request):
    date = request.query_params.get('date')
    inspector_id = request.query_params.get('inspector')
    
    filters= {}
    if date:
        filters['date']= date
    if inspector_id:
        filters['inspector_id'] = inspector_id
        
    availabilites = Availability.objects.filter(**filters)
    serializer = AvailabilitySerializer(availabilites, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)





# SALER SELECTS SLOTS
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def select_slot(request):
    user = request.user
    data = request.data
    print("Selected:",data)

    required_fields = ['saler_car_id', 'availability_id', 'time_slot']
    for field in required_fields:
        if field not in data:
            return Response({'message': f'Missing required field: {field}'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate the seller's car
    try:
        saler_car = saler_car_details.objects.get(saler_car_id=data['saler_car_id'], user=user)
    except saler_car_details.DoesNotExist:
        return Response({'message': 'Car not found or unauthorized'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate availability
    try:
        availability = Availability.objects.get(id=data['availability_id'])
    except Availability.DoesNotExist:
        return Response({'message': 'Availability not found'}, status=status.HTTP_404_NOT_FOUND)

    selected_time_slot = data['time_slot']

    # Ensure the selected slot is available
    if selected_time_slot not in availability.time_slots:
        return Response({'message': 'Selected time slot is not available'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if this slot is already booked
    if SelectedSlot.objects.filter(inspector=availability.inspector, date=availability.date, time_slot=selected_time_slot).exists():
        return Response({'message': 'Time slot already booked'}, status=status.HTTP_400_BAD_REQUEST)

    # Save the selected slot
    selected_slot = SelectedSlot(
        saler_car=saler_car,
        inspector=availability.inspector,
        date=availability.date,
        time_slot=selected_time_slot,
        booked_by="By Seller" 
    )
    selected_slot.save()

    # Remove the selected slot from availability
    availability.time_slots = [slot for slot in availability.time_slots if slot != selected_time_slot]
    availability.save()

    # Notify inspector
    notification_message = f"Appointment scheduled for {saler_car.car_name} at {selected_time_slot} on {availability.date}"
    Notification.objects.create(
        recipient=availability.inspector,
        message=notification_message,
        category='seller_time_slot_selection'
    )

    return Response({'message': 'Time slot selected successfully'}, status=status.HTTP_201_CREATED)


 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_seller_appointment_notification(request):
    user = request.user
    print("Authenticated User:", user)

    # Fetch all notifications but don't mark them as read immediately
    appointment_notifications = Notification.objects.filter(
        recipient=user,
        category="seller_time_slot_selection"
    ).order_by('-created_at')

    serializer = NotificationSerializer(appointment_notifications, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notifications_as_read(request):
    user = request.user
    Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)
    return Response({"message": "Notifications marked as read"}, status=status.HTTP_200_OK)



    
# GET SELECTED SLOTS
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_selected_slots(request):
    user = request.user
    
    # Fetch all slots selected by the current user
    selected_slots = SelectedSlot.objects.filter(saler_car__user=user)
    
    # Serialize the data
    serialized_slots = SelectedSlotSerializer(selected_slots, many=True)
    
    return Response(
        {
            'message': 'Fetched selected slots successfully',
            'slots': serialized_slots.data
        },
        status=status.HTTP_200_OK
    ) 


# get free slots of inspector
# Get free and reserved slots for an inspector
@api_view(['GET'])
@permission_classes([AllowAny])
def get_free_slots(request):
    date = request.query_params.get('date', None)
    inspector_id = request.query_params.get('inspector', None)

    if not inspector_id:
        return Response(
            {"message": "Inspector ID is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate and parse date
    if date:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"message": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        date_obj = None  # Fetch for all dates if no date is given

    # Fetch availability records
    availability_queryset = Availability.objects.filter(inspector_id=inspector_id)
    if date_obj:
        availability_queryset = availability_queryset.filter(date=date_obj)

    if not availability_queryset.exists():
        return Response(
            {"message": "No availability records found for the given inspector and date."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Fetch reserved slots
    reserved_slots_queryset = SelectedSlot.objects.filter(inspector_id=inspector_id)
    if date_obj:
        reserved_slots_queryset = reserved_slots_queryset.filter(date=date_obj)

    unique_reserved_slots = {}

    for slot in reserved_slots_queryset:
        key = (slot.date, slot.inspector, str(slot.time_slot)[:5])  # Unique identifier
        
        if key not in unique_reserved_slots:
            unique_reserved_slots[key] = {
                "slot_id": slot.id,
                "date": slot.date.strftime("%Y-%m-%d"),
                "inspector": slot.inspector.username,
                "time_slot": str(slot.time_slot)[:5],
            }

    reserved_slots = list(unique_reserved_slots.values())


    # Identify taken slots
    taken_slots = set(slot.time_slot.strftime("%H:%M") for slot in reserved_slots_queryset)

    # Fetch free slots
    free_slots = []
    for availability in availability_queryset:
        available_time_slots = availability.time_slots
        available_free_slots = [str(slot) for slot in available_time_slots if str(slot) not in taken_slots]

        for slot in available_free_slots:
            free_slots.append({
                "availability_id": availability.id,
                "date": availability.date.strftime("%Y-%m-%d"),
                "inspector": availability.inspector.username,
                "time_slot": slot  # Already stored as HH:MM
            })

    return Response(
        {
            "message": "Fetched slots successfully",
            "free_slots": free_slots,
            "reserved_slots": reserved_slots
        },
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_inspection_report(request):
    user = request.user
    if user.role != 'inspector':
        return Response({'message': 'Only inspectors can submit'}, status=status.HTTP_400_BAD_REQUEST)

    data = request.data
    print("Inspecton report:",data)

    try:
        car = saler_car_details.objects.get(saler_car_id=data['car_id'])
    except saler_car_details.DoesNotExist:
        return Response({'message': 'Car not found'}, status=status.HTTP_404_NOT_FOUND)

    # Handle Base64 Image Uploads
    car_photos = data.get('car_photos', [])  # Expecting base64 strings
    decoded_photos = []
    for index, photo in enumerate(car_photos):
        try:
            format, imgstr = photo.split(';base64,')
            ext = format.split('/')[-1]
            file_name = f"car_{car.saler_car_id}_photo_{index}.{ext}"
            decoded_photos.append(f"data:image/{ext};base64,{imgstr}")
        except Exception as e:
            return Response({'message': f"Error processing image: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    # Create Inspection Report
    report = InspectionReport.objects.create(
        inspector=user,
        saler_car=car,
        car_name=car.car_name,
        saler_demand=car.demand,
        company=car.company,
        color=car.color,
        condition=car.condition,
        model=car.model,
        fuel_type=data.get('fuel_type', ''),
        registry_number=data.get('registry_number', ''),
        year=data.get('year', 0),
        engine_capacity=data.get('engine_capacity', 0.0),
        mileage=data.get('mileage', 0.0),
        chassis_number=data.get('chassis_number', ''),
        engine_type=data.get('engine_type', ''),
        transmission_type=data.get('transmission_type', ''),
        engine_condition=data.get('engine_condition', 100),
        body_condition=data.get('body_condition', 100),
        clutch_condition=data.get('clutch_condition', 100),
        steering_condition=data.get('steering_condition', 100),
        suspension_condition=data.get('suspension_condition', 100),
        brakes_condition=data.get('brakes_condition', 100),
        ac_condition=data.get('ac_condition', 100),
        electrical_condition=data.get('electrical_condition', 100),
        estimated_value=data.get('estimated_value'),
        car_photos=decoded_photos  # Save base64 images
    )

    try:
        # 1️⃣ Notification for Car Owner (Saler)
        if car.user:
            Notification.objects.create(
                recipient=car.user,  # Check if field is spelled correctly
                message=f"Your car '{car.car_name} ({car.model})' has been inspected by {user.username}.",
                category='Your_car_inspected',
                saler_car=car,
            )
            logger.info(f"Notification sent to car owner: {car.user.username}")

        # 2️⃣ Notifications for Dealers
        dealers = User.objects.filter(role='dealer')
        logger.info(f"Found {dealers.count()} dealers.")
        for dealer in dealers:
            Notification.objects.create(
                recipient=dealer,
                message=f"The car '{car.car_name} ({car.model})' has been inspected. Check the inspection report.",
                category='dealer_car_inspected',
                saler_car=car,
            )

        # 3️⃣ Notifications for Admins
        admins = User.objects.filter(role='admin')
        logger.info(f"Found {admins.count()} admins.")
        for admin in admins:
            Notification.objects.create(
                recipient=admin,
                message=f"The car '{car.car_name} ({car.model})' has been inspected. The inspection report is available.",
                category='admin_car_inspected',
                saler_car=car,
            )

        logger.info("All notifications created successfully.")
    except Exception as e:
        logger.error(f"Error while creating notifications: {str(e)}")
    # Serialize and Return Response
    serialized_report = InspectionReportSerializer(report)
    return Response(
        {
            'message': 'Inspection report submitted successfully',
            'report': serialized_report.data
        }, 
        status=status.HTTP_201_CREATED
    )


# INSPECTION REPORT NOTIFICATION
@api_view(['GET'])
@permission_classes([AllowAny])
def get_inspection_notifications(request):
    user = request.user
    
    # For Saler: Show only their car's inspection notifications
    if user.role == 'saler':
        notifications = Notification.objects.filter(
            recipient=user,
            category='car_inspected',
            saler_car__user=user  # Ensures the car is owned by the saler
        )
    
    # For Dealer: Show inspection notifications for cars that the dealer is interested in (based on saler_car's user)
    elif user.role == 'dealer':
        notifications = Notification.objects.filter(
            recepient=user,
            category='car_inspected',
        )

    # For Admin: Show all inspection notifications
    elif user.role == 'admin':
        notifications = Notification.objects.filter(
            recepient=user,
            category='car_inspected',
        )

    else:
        return Response({'message': 'No notifications for this role'}, status=status.HTTP_403_FORBIDDEN)
    
    # Serialize notifications and return response
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)





# GET INSPECTION REPORT 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_inspection_report(request):
    car_id = request.GET.get("car_id")

    if not car_id:
        return Response({"message": "Provide Car ID"}, status=status.HTTP_400_BAD_REQUEST)

    reports = InspectionReport.objects.select_related('saler_car__user').filter(saler_car=car_id)

    if not reports.exists():
        return Response({"message": "No report found for this car"}, status=status.HTTP_404_NOT_FOUND)

    serialized_reports = InspectionReportSerializer(reports, many=True)

    return Response(serialized_reports.data, status=status.HTTP_200_OK)


# DEALERS CAN PLACE BID
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_bid(request):
    user = request.user
    
    if user.role != 'dealer':
        return Response({"message": "Only dealers can place bids"}, status=status.HTTP_403_FORBIDDEN)
    
    data = request.data
    try:
        saler_car = saler_car_details.objects.get(saler_car_id=data['saler_car'])
    except saler_car_details.DoesNotExist:
        return Response({"message": "Car not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if saler_car.is_sold:
        return Response({"message": "This car is already sold"}, status=status.HTTP_400_BAD_REQUEST)
    
    bid = Bidding.objects.create(
        
        dealer=user,
        saler_car=saler_car,
        bid_amount=data['bid_amount']
    )
    Notification.objects.create(
        recipient=saler_car.user,
        message=f"You have a new bid of {data['bid_amount']} on {saler_car.company} {saler_car.car_name}",
        saler_car=saler_car,
        category="new_bid",
        bid= bid
    )
    
    serializer = BiddingSerializer(bid)
    return Response({
        "message": "Bid placed successfully",
         "bid_id": bid.id,
        "bid": serializer.data
    }, status=status.HTTP_201_CREATED)
    
    
# FETCH BID NOTIFICATION FOR SELLER 


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bid_notification_for_seller(request):
    user = request.user

    if user.role != 'saler':
        return Response({'message': 'Only sellers can view notifications'}, status=status.HTTP_403_FORBIDDEN)

    try:
        unread_notifications = Notification.objects.filter(
            recipient=user,
            category="new_bid",
            is_read=False
        ).order_by('-created_at')

        serializer = NotificationSerializer(unread_notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'message': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_bid_notifications_as_read(request):
    user = request.user

    if user.role != 'saler':
        return Response({'message': 'Only sellers can update notifications'}, status=status.HTTP_403_FORBIDDEN)

    try:
        # Get notification IDs from request body
        notification_ids = request.data.get('notification_ids', [])

        if not notification_ids:
            return Response({'message': 'No notifications to mark as read'}, status=status.HTTP_400_BAD_REQUEST)

        # Update notifications as read
        Notification.objects.filter(id__in=notification_ids, recipient=user).update(is_read=True)

        return Response({'message': 'Notifications marked as read'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'message': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# VIEW BIDS FOR SPECEFIC CAR
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_car_bids(request , car_id):
    try:
        car = saler_car_details.objects.get(saler_car_id = car_id)
    except saler_car_details.DoesNotExist:
        return Response({"Message" : "car Not found"}, status=status.HTTP_404_NOT_FOUND)
    
    bids = Bidding.objects.filter(saler_car=car).order_by('-bid_date')
    
    serializer = BiddingSerializer(bids,many=True)
    
    return Response({"Message" : "Bids Fetched Successgully", "bids" : serializer.data},status=status.HTTP_200_OK)





# ACCEPT BID
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_bid(request,bid_id):
    user = request.user
    logger.info(f"User {user.username} is attempting to accept bid {bid_id}")

    
    try:
        bid = Bidding.objects.get(id=bid_id)
        
    except Bidding.DoesNotExist:
        logger.error(f"Bid with id {bid_id} not found.")
        return Response({"Message" : "Bid not found"},status=status.HTTP_400_BAD_REQUEST)
    
    if bid.saler_car.user != user:
        return Response({"Message" : "you are not authorized to accept bid"},status=status.HTTP_401_UNAUTHORIZED)
    
    if bid.status != "pending":
        return Response({"Message" : "Bid already processed"},status=status.HTTP_400_BAD_REQUEST)
    
    bid.is_accepted=True
    bid.status = "accepted"
    bid.save()
    
    car = bid.saler_car
    car.is_sold = True
    car.save()
    
    Bidding.objects.filter(saler_car=car).exclude(id=bid_id).update(status = "rejected")
    
    Notification.objects.create(
        recipient = bid.dealer,
        message=f"Your bid of {bid.bid_amount} on {car.company} {car.car_name} {car.model}  has been accepted.",
        saler_car = bid.saler_car,
        category = "bid_accepted"
        
    )
    
    return Response({"message" : "Bid accepted and car marked as sold"}, status=status.HTTP_200_OK)

# REJECT BID
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_bid(request, bid_id):
    user = request.user
    logger.info(f"User {user.username} is attempting to reject bid {bid_id}")

    bid = get_object_or_404(Bidding, id=bid_id)

    if bid.saler_car.user != user:
        logger.warning(f"Unauthorized bid rejection attempt by user {user.username}")
        return Response({"message": "You are not authorized to reject this bid"}, status=status.HTTP_401_UNAUTHORIZED)

    if bid.status != "pending":
        logger.info(f"Bid {bid_id} has already been processed with status {bid.status}")
        return Response({"message": "Bid has already been processed"}, status=status.HTTP_400_BAD_REQUEST)

    bid.is_accepted = False
    bid.status = "rejected"
    bid.save()

    car = bid.saler_car

    Notification.objects.create(
        recipient=bid.dealer,
        message=f"Your bid of {bid.bid_amount} on {car.company} {car.car_name} {car.model} has been rejected.",
        saler_car=car,
        bid=bid,
        category="bid_rejected"
    )

    logger.info(f"Bid {bid_id} rejected successfully by user {user.username}")
    return Response({"message": "Bid rejected"}, status=status.HTTP_200_OK)






# DEALER CAN VIEW THEIR OWN BIDS
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_dealer_bids(request):
    user = request.user
    
    if user.role != 'dealer':
        return Response({"Message" : "Onlt dealer can view their Bids"}, status=status.HTTP_400_BAD_REQUEST)
    
    bids = Bidding.objects.filter(dealer = user).order_by('-bid_date')
    serializer = BiddingSerializer(bids,many=True)
    
    return Response({"Message" : "successfuly fetched", "bids" : serializer.data},status=status.HTTP_200_OK)
    
    





# saler registe view
@api_view(['POST'])
@permission_classes([AllowAny])
def saler_register(request):
    data = request.data
    print("registed:",request.data)
    
    try:
        user = User.objects.create_user(
            username=data.get('username'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            password=data.get('password'),
            phone_number = data.get('phone_number'),
            role='saler' 
        )
        
        return Response({
            "message": "User created successfully",
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "email": user.email,
            "phone_number":user.phone_number,
            "role": user.role
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
    
    
# Saler update its details
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def saler_update(request):
    user = request.user
    
    # Ensure the user is a saler
    if user.role != 'saler':
        return Response({"message": "Only salers can update their details"}, status=status.HTTP_400_BAD_REQUEST)

    data = request.data
    
    # Update fields only if provided in the request
    user.username = data.get("username", user.username)
    user.first_name = data.get("first_name", user.first_name)
    user.last_name = data.get("last_name", user.last_name)
    user.email = data.get("email", user.email)
    user.phone_number = data.get("phone_number", user.phone_number)
    
    # Update password if provided
    if "password" in data:
        password = data.get("password")
        if password:
            user.set_password(password)  # Hash the password before saving

    try:
        user.save()
        return Response({
            "message": "User updated successfully",
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone_number": user.phone_number,
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": f"Error updating user: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
    
    
    
    
# user delete its profile
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_saler(request):
    user = request.user
    
    if user.role != 'saler':
        return Response({"Message" : "saler can delete its data"},status=status.HTTP_400_BAD_REQUEST)
    
    if request.user.id != user.id:
        return Response({"Message" : "You can delete only your data"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user_id = user.id
        user.delete()
        
        return Response({"message" : f"User witg ID {user_id} delete successfully",
                         },status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"Error": str(e)},status=status.HTTP_400_BAD_REQUEST)
        
  
  

    
# generates when saler post car details
@api_view(['GET'])
@permission_classes({IsAuthenticated})
def get_notifications(requet):
    user = requet.user
    
    notification = Notification.objects.filter(
        recipient = user,
        category = 'saler_car_details'
    )
    
    serializer = NotificationSerializer(notification,many=True)
    
    return Response(serializer.data , status=status.HTTP_200_OK)
    

# about saler car
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_as_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, recipient=request.user)
        notification.is_read = True
        notification.save()
        return Response({"message": "Notification marked as read"}, status=200)
    except Notification.DoesNotExist:
        return Response({"message": "Notification not found"}, status=404)
       
    
# get the list of all cars by sellers
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cars_list(request):
    
    cars = saler_car_details.objects.all()
    serializer = SalerCarDetailsSerializer(cars,many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# fetch assign slots  
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_assigned_slots(request):
    user = request.user

    if user.role == 'inspector':
        slots = SelectedSlot.objects.filter(inspector=user)
    elif user.role == 'saler':
        slots = SelectedSlot.objects.filter(saler_car__user=user)
    else:
        return Response({"message": "Unauthorized role."}, status=status.HTTP_403_FORBIDDEN)

    # Serialize the slots
    serializer = SelectedSlotSerializer(slots, many=True)
    return Response(
        {
            "message": "Assigned slots fetched successfully.",
            "slots": serializer.data,
        },
        status=status.HTTP_200_OK,
    )
   
   
   
    
# notifciation of appointment
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_appointment_notification(request):
    
    user = request.user
    
    notifications = Notification.objects.filter(
        recepient = user,
        category = 'inspector_gives_appointment'
    ).order_by('-created_at')
    
    serializer = NotificationSerializer(notifications,many=True)
    return Response({
        "message" : "Appointment",
        "notification": serializer.data
    },
      status=status.HTTP_200_OK
      )
    
# SALER UPDATED CAR DETAILS
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_car_details(request, car_id):
    user = request.user
    
    if user.role != 'saler':
        return Response("only Sler can update", status=status.HTTP_400_BAD_REQUEST)
    
    try:
        saler_car = saler_car_details.objects.get(saler_car_id = car_id,user=user)
    except saler_car_details.DoesNotExist:
        return Response("Car not found",status=status.HTTP_404_NOT_FOUND)
    
    saler_phone_number = user.phone_number
    
    old_car_details = saler_car.__dict__.copy()
    
    serializer = SalerCarDetailsSerializer(saler_car,data=request.data,partial=True)
    
    if serializer.is_valid():
        updated_car = serializer.save()
        
        if old_car_details != updated_car.__dict__:
            notifications = Notification.objects.filter(saler_car=saler_car)
            for notification in notifications:
                notification.message = (
                    f"Updated car details for {updated_car.car_name}: "
                    f"New demand {updated_car.demand} and phone number {saler_phone_number}."
                )
                notification.save()
                
        return Response({
            "message" : "Updated successfully",
            "result" : serializer.data
            
        },status=status.HTTP_201_CREATED)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    
# SALER SEE ONLY ITS APPOINTMENT WITH INSPECTOR

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def saler_appointmet(request):
    user = request.user
    
    if user.role != 'saler':
        return Response({"Message": "Only Saler can view their appointment"}, status=status.HTTP_403_FORBIDDEN)
    
    # Fetch all appointments related to the seller
    appointments = SelectedSlot.objects.filter(saler_car__user=user).select_related("saler_car", "inspector")
    
    appointments_data = []
    
    for appointment in appointments:
        # Convert date & time to a timezone-aware datetime object
        appointment_datetime = timezone.make_aware(
            datetime.combine(appointment.date, appointment.time_slot)
        )

        # Calculate remaining time
        remaining_seconds = (appointment_datetime - timezone.now()).total_seconds()
        remaining_days = int(remaining_seconds // (24 * 3600))  # Convert to days
        remaining_hours = int((remaining_seconds % (24 * 3600)) // 3600)  # Convert remainder to hours
        remaining_minutes = int((remaining_seconds % 3600) // 60)  # Convert remainder to minutes
        remaining_secs = int(remaining_seconds % 60)  # Remaining seconds

        # Append data to list
        appointments_data.append({
            "appointment_id": appointment.id,
            "car_name": appointment.saler_car.car_name,
            "company": appointment.saler_car.company,
            "car_year": appointment.saler_car.model,
            "appointment_date": appointment.date.strftime("%Y-%m-%d"),
            "car_photos":appointment.saler_car.photos,
            "appointment_time": appointment.time_slot.strftime("%H:%M"),
            "inspector_first_name": appointment.inspector.first_name,
            "inspector_last_name": appointment.inspector.last_name,
            "inspector_phone_number": appointment.inspector.phone_number,
            "inspector_adress":appointment.inspector.adress,
            "inspector_email": appointment.inspector.email,
            "remaining_days": remaining_days,
            "remaining_hours": remaining_hours,
            "remaining_minutes": remaining_minutes,
            "remaining_seconds": remaining_secs
        })
    
    # Return all appointments in response
    return Response({"appointments": appointments_data}, status=status.HTTP_200_OK)


# INSPECTOR CAN SEE ALL APPOINTMENTS


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inspector_appointments(request):
    """ Fetch all appointments for an inspector where the seller is not null. """
    user = request.user

    if user.role != 'inspector':
        return Response({"message": "Only inspectors can view this data"}, status=status.HTTP_403_FORBIDDEN)

    # Fetch appointments where the seller is not null
    appointments = SelectedSlot.objects.filter(
        inspector=user, 
        saler_car__user__isnull=False
    ).order_by('date', 'time_slot')  # Order by date and time

    if not appointments.exists():
        return Response({"message": "No valid appointments found for this inspector"}, status=status.HTTP_404_NOT_FOUND)

    unique_appointments = {}
    now = timezone.now()

    for appointment in appointments:
        car_id = appointment.saler_car.saler_car_id

        # Keep only the first occurrence of each car_id
        if car_id not in unique_appointments:
            appointment_datetime = datetime.combine(appointment.date, appointment.time_slot)

            # If the datetime is not timezone-aware, make it aware
            if timezone.is_naive(appointment_datetime):
                appointment_datetime = timezone.make_aware(appointment_datetime)

            remaining_seconds = max(0, int((appointment_datetime - now).total_seconds()))

            # Convert seconds into days, hours, minutes, and seconds
            remaining_days = remaining_seconds // (24 * 3600)
            remaining_hours = (remaining_seconds % (24 * 3600)) // 3600
            remaining_minutes = (remaining_seconds % 3600) // 60
            remaining_secs = remaining_seconds % 60

            unique_appointments[car_id] = {
                "appointment_id": appointment.id,
                "car_id": car_id,
                "seller_first_name": appointment.saler_car.user.first_name if appointment.saler_car.user else "N/A",
                "seller_last_name": appointment.saler_car.user.last_name if appointment.saler_car.user else "N/A",
                "seller_phone_number": appointment.saler_car.user.phone_number if appointment.saler_car.user else "N/A",
                "seller_email": appointment.saler_car.user.email if appointment.saler_car.user else "N/A",
                "car_name": appointment.saler_car.car_name,
                "car_company": appointment.saler_car.company,
                "car_photos": [
                    f"data:image/jpeg;base64,{photo}" if not photo.startswith("data:image") else photo 
                    for photo in appointment.saler_car.photos
                ],  # Ensure Base64 prefix exists
                "car_model": appointment.saler_car.model,
                "date": appointment.date.strftime("%Y-%m-%d"),
                "time_slot": appointment.time_slot.strftime("%H:%M:%S"),
                "remaining_days": remaining_days,
                "remaining_hours": remaining_hours,
                "remaining_minutes": remaining_minutes,
                "remaining_seconds": remaining_secs,
                "selected_by": appointment.booked_by,
                "is_inspected": appointment.saler_car.is_inspected
            }

    return Response({
        "message": "Inspector appointments retrieved successfully",
        "appointments": list(unique_appointments.values())
    }, status=status.HTTP_200_OK)




@api_view(["POST"])
@permission_classes([IsAuthenticated])
def assign_slot(request):
    print("Received data:", json.dumps(request.data, indent=2))

    if "car_id" not in request.data:
        return Response({"error": "Car ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    data = request.data.copy()
    data["inspector_id"] = request.user.id  # Assign inspector ID

    try:
        car = saler_car_details.objects.get(saler_car_id=data["car_id"])
    except saler_car_details.DoesNotExist:
        return Response({"error": "Invalid Car ID"}, status=status.HTTP_400_BAD_REQUEST)

    data["car"] = car.saler_car_id  # Assign car ID

    serializer = AssignedSlotSerializer(data=data, context={"request": request})

    if serializer.is_valid():
        assigned_slot = serializer.save()

        # ✅ Ensure time slot is stored in HH:MM format
        assigned_slot.time_slot = assigned_slot.time_slot.strftime("%H:%M")
        assigned_slot.save(update_fields=["time_slot"])

        # ✅ Create a SelectedSlot record
        SelectedSlot.objects.create(
            inspector=assigned_slot.inspector,
            saler_car=assigned_slot.car,
            date=assigned_slot.date,
            time_slot=assigned_slot.time_slot  # HH:MM format
        )

        # ✅ Find and update Availability to remove the assigned slot
        try:
            availability = Availability.objects.get(inspector=assigned_slot.inspector, date=assigned_slot.date)
            
            # ✅ Ensure all time slots are in HH:MM format
            availability.time_slots = [slot.strftime("%H:%M") if isinstance(slot, datetime) else slot for slot in availability.time_slots]

            # ✅ Remove the selected slot
            if assigned_slot.time_slot in availability.time_slots:
                availability.time_slots.remove(assigned_slot.time_slot)
                availability.save(update_fields=["time_slots"])  # ✅ Save only the modified field

        except Availability.DoesNotExist:
            return Response({"error": "Availability record not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(AssignedSlotSerializer(assigned_slot).data, status=status.HTTP_201_CREATED)
    else:
        print("Errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_assigned_slots(request):
    assigned_slots = AssignSlot.objects.select_related(
        "car", "car__guest", "inspector"
    ).filter(car__guest__isnull=False)  # ✅ Only include slots where guest exists

    serializer = AssignedSlotSerializer(assigned_slots, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



# additional name and number post view 
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def post_additional_details(request):
    serializer = AdditionalDetailSerializer(data = request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response({"Message" : "Data saved", "data" : serializer.data},status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([AllowAny])  # Allow public access
def post_guest_details(request):
    serializer = GuestSerializer(data=request.data)
    print(request.data)

    if serializer.is_valid():
        guest = serializer.save()
        return Response({"Message": "Data saved",
                         "guest_id": guest.id,
                         "data": serializer.data}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# list of saler cars
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_cars(request):

    user = request.user  
    cars = saler_car_details.objects.filter(user=user).select_related("user")

    serializer = SalerCarDetailsSerializer(cars, many=True)
    return Response({"cars": serializer.data}, status=status.HTTP_200_OK)

# update the car status 
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_status(request, car_id):
    try:
        car = saler_car_details.objects.get(saler_car_id = car_id)
        new_status = request.data.get("status")
        print("staus:",new_status)
        
        valid_status = dict(saler_car_details.STATUS_CHOICES).keys()
        if new_status not in valid_status:
            return Response({"Error" : "invalid Status"},status=status.HTTP_400_BAD_REQUEST)
        car.status = new_status
        car.save()
        
        return Response({"message" : "Status updated successfully", "new status" : car.status}, status=status.HTTP_200_OK)
    
    except saler_car_details.DoesNotExist:
        return Response({"Error" : "Not Found"}, status=status.HTTP_404_NOT_FOUND)
    
    
# fetch cars list for dealer with status bidding
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_bidding_cars(request):
    user = request.user

    if user.role != 'dealer':
        return Response({"message": "Only dealers can view this"}, status=status.HTTP_403_FORBIDDEN)

    cars = saler_car_details.objects.select_related('user').filter(status='bidding')

    if not cars.exists():
        return Response({"error": "No cars found in bidding status"}, status=status.HTTP_404_NOT_FOUND)

    data = []
    for car in cars:
        # Get latest inspection report if available
        inspection_report = car.inspection_reports.order_by('-inspection_date').first()

        data.append({
            "saler_car_id": car.saler_car_id,
            "car_name": car.car_name,
            "company": car.company,
            "model": car.model,
            "demand": car.demand,
            "photos": car.photos,
            "overall_rating": inspection_report.overall_score if inspection_report else None,  
        })

    return Response({"message": "Cars fetched successfully", "cars": data}, status=status.HTTP_200_OK)




# get cars with status inspection for dealer (upcoming)
@api_view(["GET"])
@permission_classes([IsAuthenticated])

def get_upcoming_cars(request):
    try:
        cars = saler_car_details.objects.filter(status="pending")
        
        if not cars.exists():
            return Response({"Message" : "No Upcoming cars Found!"}, status=status.HTTP_404_NOT_FOUND) 
        
        serializer = SalerCarDetailsSerializer(cars, many=True)
        
        return Response({"cars":serializer.data}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"message" : str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
# accept inspection
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_inspection(request , report_id):
    report = get_object_or_404(InspectionReport , id=report_id)
    report.approve_inspection()
    return Response({"message" : "Car is Approved by admin, now in Bidding"}, status=status.HTTP_201_CREATED)

#reject inspection
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_inspection(request , report_id):
    report = get_object_or_404(InspectionReport , id=report_id)
    report.reject_inspection()
    return Response({"message" : "Car is rejected by admin"}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_cars_for_approval(request):
    try:
        cars = saler_car_details.objects.filter(status="await_approval")
        
        if not cars.exists():
            return Response({"message" : "car not found"}, status=status.HTTP_404_NOT_FOUND)
        
        
        serializer = SalerCarDetailsSerializer(cars, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e :
        return Response({"message" : str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
# get seller manual entries 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def seller_manual_entries(request):
    try:
        inspector_id = request.GET.get('inspector_id')  # Get inspector ID from request

        if not inspector_id:
            return Response({"error": "Inspector ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate that the user is an inspector
        try:
            inspector = User.objects.get(id=inspector_id, role__iexact="Inspector")
        except User.DoesNotExist:
            return Response({"error": "Invalid inspector ID"}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Fetch only cars added by a **Seller** (Exclude guest cars)
        linked_cars = saler_car_details.objects.filter(
            inspector=inspector, 
            user__isnull=False, 
            guest__isnull=True,  # Ensure it's not a guest car
            status='pending'
        ).distinct()  # Avoid duplicate records

        # Serialize the data
        serializer = SalerCarDetailsSerializer(linked_cars, many=True)
        return Response({"success": True, "linked_cars": serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Error in seller_manual_entries: {e}")  # Debugging
        return Response(
            {'success': False, 'message': f'Error retrieving linked cars: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
# ///////admin///////


#cars count with status bidding

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_bidding_cars_count(request):
    try:
        user = request.user
        
        # Check if user is an admin
        if user.role.lower() != 'admin':  
            return Response({"message": "Only admin can view this."}, status=status.HTTP_403_FORBIDDEN)
        
        # Count cars in bidding status
        bidding_cars_count = saler_car_details.objects.filter(status='bidding').count()
        
        return Response({"bidding_cars_count": bidding_cars_count}, status=status.HTTP_200_OK)
    except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# get highest bid
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_highest_bid(request):
    try:
        user = request.user
        if user.role != 'admin':
            return Response({"message" : "only dealer can view"}, status=status.HTTP_403_FORBIDDEN)
        
        highest_bid = Bidding.objects.aggregate(Max('bid_amount'))['bid_amount__max']
        
        if highest_bid is None:
            return Response({'highest_bid_amount' : 0},status=status.HTTP_200_OK)
        
        return Response({'highest_bid_amount' : highest_bid},status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

        


