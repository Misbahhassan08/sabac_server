from django.db.models.functions import TruncWeek, TruncDay, TruncMonth

# from sabac.services.user_migration import migrate_guest_to_user
from django.db.models import Count
from django.contrib.auth import get_user_model
from testcase import my_default_json, merge_json
from time import timezone
from django.utils.timezone import localtime, now
from venv import logger
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .serializers import (
    UserSerializer,
    SalerCarDetailsSerializer,
    AvailabilitySerializer,
    SelectedSlotSerializer,
    InspectionReportSerializer,
    BiddingSerializer,
    NotificationSerializer,
    AssignedSlotSerializer,
    AdditionalDetailSerializer,
    GuestSerializer,
    DeviceTokenSerializer,
)
from .models import (
    User,
    saler_car_details,
    Availability,
    SelectedSlot,
    InspectionReport,
    Bidding,
    Notification,
    InspectionReportNotification,
    AssignSlot,
    AdditionalDetails,
    Guest,
    DeviceToken,
)
from rest_framework import status
from datetime import datetime
from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
import logging
from django.db.models import Max
from rest_framework_simplejwt.tokens import RefreshToken


logger = logging.getLogger(__name__)

# login


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        try:
            username_or_email = request.data.get("username_or_email")
            device_id = request.data.get("device_id")

            if not device_id:
                return Response(
                    {"success": False, "message": "device_id is required"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Identify user
            if "@" in username_or_email:
                user = User.objects.get(email=username_or_email)
            else:
                user = User.objects.get(username=username_or_email)

            request.data["username"] = user.username

            if user.role == "dealer":
                existing_devices = DeviceToken.objects.filter(user=user)

                if (
                    existing_devices.count() >= 3
                    and not existing_devices.filter(device_id=device_id).exists()
                ):
                    return Response(
                        {
                            "success": False,
                            "message": "Maximum number of devices reached. Please logout from another device to continue.",
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

            response = super().post(request, *args, **kwargs)
            if response.status_code != 200 or "access" not in response.data:
                return Response(
                    {"success": False, "message": "Invalid credentials"}, status=401
                )

            tokens = response.data

            token_entry, created = DeviceToken.objects.update_or_create(
                user=user,
                device_id=device_id,
                defaults={"token": tokens["refresh"]},
            )

            user_serializer = UserSerializer(user)

            res = Response(
                {
                    "success": True,
                    "access_token": tokens["access"],
                    "refresh_token": tokens["refresh"],
                    "user": user_serializer.data,
                }
            )

            res.set_cookie(
                key="access_token",
                value=tokens["access"],
                httponly=True,
                secure=True,
                samesite="Lax",
                path="/",
            )
            res.set_cookie(
                key="refresh_token",
                value=tokens["refresh"],
                httponly=True,
                secure=True,
                samesite="Lax",
                path="/",
            )

            return res

        except ObjectDoesNotExist:
            return Response({"success": False, "error": "User not found"}, status=404)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=400)


# refreshing the access token
class CustomRefreshTokenView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get("refresh_token")
            if not refresh_token:
                return Response({"refreshed": False, "error": "No refresh token found"})

            request.data["refresh"] = refresh_token
            response = super().post(request, *args, **kwargs)
            tokens = response.data

            res = Response()
            res.data = {"refreshed": True, "access_token": tokens["access"]}

            res.set_cookie(
                key="access_token",
                value=tokens["access"],
                httponly=True,
                secure=True,
                samesite="Lax",
                path="/",
            )
            return res
        except Exception as e:
            return Response({"refreshed": False, "error": str(e)})


# LOgout
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get("refresh_token")
        device_id = request.data.get("device_id")

        if not refresh_token or not device_id:
            return Response(
                {"success": False, "error": "refresh_token and device_id are required"},
                status=400,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response({"success": False, "error": "Invalid token"}, status=400)

        # Remove device entry
        DeviceToken.objects.filter(user=request.user, device_id=device_id).delete()

        response = Response({"success": True, "message": "Logged out successfully"})
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response

    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=400)


# for check authentecated


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def is_authentecated(request):
    return Response({"authentecation": True})


# ////////////////////////////////////////ADMIN APIs///////////////////////////////////////////////////////////


# cars count with status bidding
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_cars_count(request):
    try:
        user = request.user
        if user.role.lower() != "admin":
            return Response(
                {"message": "Only admin can view this."},
                status=status.HTTP_403_FORBIDDEN,
            )
        total_cars = saler_car_details.objects.all().count()
        bidding_cars_count = saler_car_details.objects.filter(status="bidding").count()
        pending_cars_count = saler_car_details.objects.filter(status="pending").count()
        sold_cars = saler_car_details.objects.filter(status="sold").count()

        return Response(
            {
                "bidding_cars_count": bidding_cars_count,
                "total_cars": total_cars,
                "pending_cars_count": pending_cars_count,
                "sold_cars": sold_cars,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response(
            {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# get highest bid


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_highest_bid(request):
    try:
        user = request.user
        if user.role != "admin":
            return Response(
                {"message": "only admin can view"}, status=status.HTTP_403_FORBIDDEN
            )

        highest_bid = Bidding.objects.aggregate(Max("bid_amount"))["bid_amount__max"]

        if highest_bid is None:
            return Response({"highest_bid_amount": 0}, status=status.HTTP_200_OK)

        return Response({"highest_bid_amount": highest_bid}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# get list of cars accepted or rejected


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_reviewd_inspection(request):
    try:
        user = request.user
        if user.role != "admin":
            return Response(
                {"message": "only admin can view"}, status=status.HTTP_403_FORBIDDEN
            )
        cars = saler_car_details.objects.filter(
            Q(is_accepted=True) | Q(is_rejected=True)
        )

        serializer = SalerCarDetailsSerializer(cars, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# car list with status awaiting approval


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_cars_for_approval(request):
    try:
        cars = saler_car_details.objects.filter(status="await_approval")

        if not cars.exists():
            return Response(
                {"message": "car not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = SalerCarDetailsSerializer(cars, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# accept inspection


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def approve_inspection(request, report_id):
    report = get_object_or_404(InspectionReport, id=report_id)
    report.approve_inspection()
    return Response(
        {"message": "Car is Approved by admin, now in Bidding"},
        status=status.HTTP_201_CREATED,
    )


# reject inspection


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reject_inspection(request, report_id):
    report = get_object_or_404(InspectionReport, id=report_id)
    report.reject_inspection()
    return Response(
        {"message": "Car is rejected by admin"}, status=status.HTTP_201_CREATED
    )


# get the list of all cars by sellers TOTAL CARS IN DATABSE NOT USED


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_cars_list(request):

    cars = saler_car_details.objects.all()
    serializer = SalerCarDetailsSerializer(cars, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ADMIN REGISTER THE DEALER AND INSPECTOR


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register(request):
    allowed_roles = ["dealer", "inspector", "admin"]

    role = request.data.get("role")

    if role not in allowed_roles:
        return ValidationError(
            {"role": f"invalid Role. Allowed Roles are: {','.join(allowed_roles)}"}
        )

    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)


# ADMIN UPDATE THE SALER & INSPECTOR


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def edit_user(request):
    admin = request.user

    user_id = request.data.get("id")
    if not user_id:
        return Response(
            {"message": "User ID is required to edit a user."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user_to_edit = User.objects.get(id=user_id)

        if user_to_edit != admin and admin.role != "admin":
            return Response(
                {"message": "Only admins can edit other users."},
                status=status.HTTP_403_FORBIDDEN,
            )

        data = request.data
        user_to_edit.username = data.get("username", user_to_edit.username)
        user_to_edit.first_name = data.get("first_name", user_to_edit.first_name)
        user_to_edit.last_name = data.get("last_name", user_to_edit.last_name)
        user_to_edit.email = data.get("email", user_to_edit.email)
        user_to_edit.phone_number = data.get("phone_number", user_to_edit.phone_number)

        if user_to_edit != admin:
            new_role = data.get("role")
            allowed_roles = ["dealer", "inspector", "admin"]
            if new_role and new_role in allowed_roles:
                user_to_edit.role = new_role
            elif new_role:
                return Response(
                    {
                        "message": f"Invalid role. Allowed roles are: {', '.join(allowed_roles)}"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        user_to_edit.save()

        return Response(
            {
                "message": "User updated successfully.",
                "id": user_to_edit.id,
                "username": user_to_edit.username,
                "first_name": user_to_edit.first_name,
                "last_name": user_to_edit.last_name,
                "email": user_to_edit.email,
                "phone_number": user_to_edit.phone_number,
                "role": user_to_edit.role,
            },
            status=status.HTTP_200_OK,
        )
    except User.DoesNotExist:
        return Response(
            {"message": "User not found."}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"message": f"Error updating user: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )


# ADMIN DELETE THE USERS


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_user(request):
    admin = request.user

    if admin.role != "admin":
        return Response({"message": "only admin can delete"})

    user_id = request.data.get("id")
    if not user_id:
        return Response({"message": "user Id is required to delete user"})

    try:
        user_to_delete = User.objects.get(id=user_id)

        user_to_delete.delete()

        return Response(
            {"message": f"user with ID {user_id} deleted successfully"},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# get LIST OF ALL users


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def usersList(request):
    try:

        if not request.user.is_authenticated:
            return Response(
                {"success": False, "message": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if request.user.role != "admin":
            logger.warning(f"Unauthorized access attempt by user: {request.user.email}")
            return Response(
                {
                    "success": False,
                    "message": "You are not authorized. Only admins can access this resource.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # 2. Fetch all users (optimized query)
        users = User.objects.all().only(
            "id", "email", "role", "username"
        )  # Select only needed fields

        # 3. Serialize data
        serializer = UserSerializer(users, many=True)

        # 4. Return successful response
        return Response(
            {
                "success": True,
                "users": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"Error in usersList API: {str(e)}", exc_info=True)
        return Response(
            {
                "success": False,
                "message": "An unexpected error occurred while fetching users.",
                "error": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# list of dealrs


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dealersList(request):
    try:
        if not request.user.is_authenticated:
            return Response(
                {"success": False, "message": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if request.user.role != "admin":
            logger.warning(f"Unauthorized access attempt by user: {request.user.email}")
            return Response(
                {
                    "success": False,
                    "message": "You are not authorized. Only admins can access this resource.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # 🔍 Filter only dealers and return all fields
        users = User.objects.filter(role="dealer")

        # Serialize all fields
        serializer = UserSerializer(users, many=True)

        return Response(
            {
                "success": True,
                "dealers": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"Error in usersList API: {str(e)}", exc_info=True)
        return Response(
            {
                "success": False,
                "message": "An unexpected error occurred while fetching users.",
                "error": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# list of inspectors


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def inspectorsList(request):
    try:
        if not request.user.is_authenticated:
            return Response(
                {"success": False, "message": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if request.user.role != "admin":
            logger.warning(f"Unauthorized access attempt by user: {request.user.email}")
            return Response(
                {
                    "success": False,
                    "message": "You are not authorized. Only admins can access this resource.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # 🔍 Filter only dealers and return all fields
        users = User.objects.filter(role="inspector")

        # Serialize all fields
        serializer = UserSerializer(users, many=True)

        return Response(
            {
                "success": True,
                "inspectors": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"Error in API: {str(e)}", exc_info=True)
        return Response(
            {
                "success": False,
                "message": "An unexpected error occurred while fetching users.",
                "error": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# list of admins


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def adminList(request):
    try:
        if not request.user.is_authenticated:
            return Response(
                {"success": False, "message": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if request.user.role != "admin":
            logger.warning(f"Unauthorized access attempt by user: {request.user.email}")
            return Response(
                {
                    "success": False,
                    "message": "You are not authorized. Only admins can access this resource.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # 🔍 Filter only dealers and return all fields
        users = User.objects.filter(role="admin")

        # Serialize all fields
        serializer = UserSerializer(users, many=True)

        return Response(
            {
                "success": True,
                "admins": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"Error in API: {str(e)}", exc_info=True)
        return Response(
            {
                "success": False,
                "message": "An unexpected error occurred while fetching users.",
                "error": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# count of users


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_count(request):
    try:
        if request.user.role != "admin":
            return Response(
                {"message": "only admin can access"}, status=status.HTTP_403_FORBIDDEN
            )

        total = User.objects.count()
        sellers = User.objects.filter(role="saler").count()
        inspector = User.objects.filter(role="inspector").count()
        dealer = User.objects.filter(role="dealer").count()
        admin = User.objects.filter(role="admin").count()

        data = {
            "total_users": total,
            "sellers": sellers,
            "inspector": inspector,
            "dealer": dealer,
            "admin": admin,
        }

        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# count of cars


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_cars_count(request):
    try:
        if request.user.role != "admin":
            return Response(
                {"message": "Only admin can access"}, status=status.HTTP_403_FORBIDDEN
            )

        total = saler_car_details.objects.count()
        pending = saler_car_details.objects.filter(status="pending").count()
        assigned = saler_car_details.objects.filter(status="assigned").count()
        in_inspection = saler_car_details.objects.filter(status="in_inspection").count()
        awaiting_approval = saler_car_details.objects.filter(
            status="await_approval"
        ).count()
        rejected = saler_car_details.objects.filter(status="rejected").count()
        bidding = saler_car_details.objects.filter(status="bidding").count()
        expired = saler_car_details.objects.filter(status="expired").count()
        sold = saler_car_details.objects.filter(status="sold").count()

        data = {
            "total_cars": total,
            "pending": pending,
            "assigned": assigned,
            "in_inspection": in_inspection,
            "awaiting_approval": awaiting_approval,
            "rejected": rejected,
            "bidding": bidding,
            "expired": expired,
            "sold": sold,
        }
        return Response(data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# car posting graph daily weekly


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def carsStats(request):
    range_type = request.GET.get("range", "daily")
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    queryset = saler_car_details.objects.all()

    if from_date and to_date:
        try:
            from_date_obj = datetime.strptime(from_date, "%Y-%m-%d")
            to_date_obj = datetime.strptime(to_date, "%Y-%m-%d")
            queryset = queryset.filter(
                created_at__date__gte=from_date_obj, created_at__date__lte=to_date_obj
            )
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    if range_type == "weekly":
        queryset = queryset.annotate(period=TruncWeek("created_at"))

    elif range_type == "monthly":
        queryset = queryset.annotate(period=TruncMonth("created_at"))

    elif range_type == "15days":
        queryset = queryset.extra(
            select={
                "period": "DATE_TRUNC('day', created_at) - INTERVAL '1 day' * (EXTRACT(DAY FROM created_at)::int % 15)"
            }
        )

    elif range_type == "3months":
        queryset = queryset.extra(
            select={
                "period": "DATE_TRUNC('month', created_at) - INTERVAL '1 month' * (EXTRACT(MONTH FROM created_at)::int % 3)"
            }
        )

    elif range_type == "6months":
        queryset = queryset.extra(
            select={
                "period": "DATE_TRUNC('month', created_at) - INTERVAL '1 month' * (EXTRACT(MONTH FROM created_at)::int % 6)"
            }
        )

    elif range_type == "1year":
        queryset = queryset.extra(select={"period": "DATE_TRUNC('year', created_at)"})

    elif range_type == "complete":
        total = queryset.count()
        return Response(
            [{"period": "Complete", "count": total}], status=status.HTTP_200_OK
        )

    else:
        queryset = queryset.annotate(period=TruncDay("created_at"))

    data = (
        queryset.values("period")
        .annotate(count=Count("saler_car_id"))
        .order_by("period")
    )
    return Response(data, status=status.HTTP_200_OK)


# ACCEPT BID


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_bid(request, bid_id):
    user = request.user
    logger.info(f"User {user.username} is attempting to accept bid {bid_id}")

    if user.role != "admin":
        return Response(
            {"message": "Only admins can accept bids"},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        bid = Bidding.objects.get(id=bid_id)
    except Bidding.DoesNotExist:
        logger.error(f"Bid with id {bid_id} not found.")
        return Response({"message": "Bid not found"}, status=status.HTTP_404_NOT_FOUND)

    if bid.status != "pending":
        return Response(
            {"message": "Bid already processed"}, status=status.HTTP_400_BAD_REQUEST
        )

    bid.is_accepted = True
    bid.status = "accepted"
    bid.save()

    car = bid.saler_car
    car.is_sold = True
    car.winner_dealer = bid.dealer
    car.save()

    # Reject other bids
    Bidding.objects.filter(saler_car=car).exclude(id=bid_id).update(status="rejected")

    # Notify dealer
    Notification.objects.create(
        recipient=bid.dealer,
        message=f"Your bid of {bid.bid_amount} on {car.company} {car.car_name} {car.year} has been accepted.",
        saler_car=car,
        bid=bid,
        category="bid_accepted",
    )

    return Response(
        {"message": "Bid accepted and car marked as sold"},
        status=status.HTTP_200_OK,
    )


# REJECT BID
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reject_bid(request, bid_id):
    user = request.user
    logger.info(f"User {user.username} is attempting to reject bid {bid_id}")

    if user.role != "admin":
        return Response(
            {"message": "Only admins can reject bids"},
            status=status.HTTP_403_FORBIDDEN,
        )

    bid = get_object_or_404(Bidding, id=bid_id)

    if bid.status != "pending":
        logger.info(f"Bid {bid_id} has already been processed with status {bid.status}")
        return Response(
            {"message": "Bid has already been processed"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    bid.is_accepted = False
    bid.status = "rejected"
    bid.save()

    car = bid.saler_car

    Notification.objects.create(
        recipient=bid.dealer,
        message=f"Your bid of {bid.bid_amount} on {car.company} {car.car_name} {car.year} has been rejected.",
        saler_car=car,
        bid=bid,
        category="bid_rejected",
    )

    logger.info(f"Bid {bid_id} rejected successfully by admin {user.username}")
    return Response({"message": "Bid rejected"}, status=status.HTTP_200_OK)


# FETCH BID NOTIFICATION FOR admin not used


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def bid_notification(request):
    user = request.user

    if user.role != "admin":
        return Response(
            {"message": "Only admin can view notifications"},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        unread_notifications = Notification.objects.filter(
            recipient=user, category="new_bid", is_read=False
        ).order_by("-created_at")

        serializer = NotificationSerializer(unread_notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"message": f"Error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# FETCH BID NOTIFICATION FOR admin


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def bid_notification_for_seller(request):
    user = request.user
    if user.role != "admin":
        return Response(
            {"message": "Only admin can view notifications"},
            status=status.HTTP_403_FORBIDDEN,
        )
    try:
        unread_notifications = Notification.objects.filter(
            recipient=user, category="new_bid", is_read=False
        ).order_by("-created_at")
        serializer = NotificationSerializer(unread_notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"message": f"Error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_bid_notifications_as_read(request):
    user = request.user

    if user.role != "admin":
        return Response(
            {"message": "Only admins can update bid notifications"},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        notification_ids = request.data.get("notification_ids", [])

        if not notification_ids:
            return Response(
                {"message": "No notifications to mark as read"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated_count = Notification.objects.filter(
            id__in=notification_ids, recipient=user, category="new_bid"
        ).update(is_read=True)

        return Response(
            {"message": f"{updated_count} notifications marked as read"},
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"message": f"Error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# admin view all bids
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_bidding(request):
    user = request.user

    if user.role != "admin":
        return Response(
            {"success": False, "message": "Only admin can view all bids."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:

        bids = Bidding.objects.select_related("dealer", "saler_car", "saler_car__user")

        serializer = BiddingSerializer(bids, many=True)

        return Response(
            {
                "success": True,
                "message": "All bids fetched successfully.",
                "bids": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"Error fetching all bids for admin: {str(e)}", exc_info=True)
        return Response(
            {
                "success": False,
                "message": "An unexpected error occurred while fetching bids.",
                "error": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# admin view all sold cars
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_sold_cars(request):

    sold_cars = saler_car_details.objects.filter(status="sold", is_sold=True)

    result = []

    for car in sold_cars:
        accepted_bid = Bidding.objects.filter(saler_car=car, is_accepted=True).first()

        result.append(
            {
                "car_id": car.saler_car_id,
                "car_name": car.car_name,
                "company": car.company,
                "photos": car.photos if car.photos else [],
                "year": car.year,
                "owner": (
                    {
                        "id": car.user.id,
                        "username": car.user.username,
                        "first_name": car.user.first_name,
                        "last_name": car.user.last_name,
                        "adress": car.user.adress,
                        "number": car.user.phone_number,
                    }
                    if car.user
                    else None
                ),
                "winner_dealer": (
                    {
                        "id": car.winner_dealer.id,
                        "username": car.winner_dealer.username,
                        "first_name": car.winner_dealer.first_name,
                        "last_name": car.winner_dealer.last_name,
                        "adress": car.winner_dealer.adress,
                        "number": car.winner_dealer.phone_number,
                    }
                    if car.winner_dealer
                    else None
                ),
                "accepted_bid_amount": (
                    str(accepted_bid.bid_amount) if accepted_bid else None
                ),
                "accepted_bid_date": accepted_bid.bid_date if accepted_bid else None,
            }
        )
        return Response(result)


# /////////////////////////////////////SELLER APIs/////////////////////////////////////////


# seller post car detail
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_car_details(request):
    try:
        user = request.user
        data = request.data.copy()
        print("car data",data)
        data["user"] = user.id
        data["added_by"] = "seller"

        serializer = SalerCarDetailsSerializer(data=data)
        if serializer.is_valid():
            car_details = serializer.save()

            saler_phone_number = getattr(user, "phone_number", "N/A")

            inspection_date = car_details.inspection_date.strftime("%Y-%m-%d")
            # inspection_time = car_details.inspection_time.strftime("%I:%M %p")
            inspection_time = car_details.inspection_time


            inspectors = User.objects.filter(role="inspector")

            for inspector in inspectors:
                notification = Notification.objects.create(
                    recipient=inspector,
                    message=(
                        f"New Car: {car_details.car_name} ({car_details.year})"
                        f"Added by: {user.username} (Phone: {saler_phone_number})"
                        f"Inspection Scheduled: {inspection_date} at {inspection_time}"
                    ),
                    category="saler_car_details",
                )
                print(
                    f"Created Notification ID: {notification.id} for inspector: {inspector.username}"
                )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        print("Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print(f"Error in add_car_details view: {str(e)}")
        return Response(
            {"success": False, "message": "An error occurred while adding car details"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# SALER SELECTS SLOTS


# seller select slot
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def select_slot(request):
    user = request.user
    data = request.data

    required_fields = ["saler_car_id", "availability_id", "time_slot"]
    for field in required_fields:
        if field not in data:
            return Response(
                {"message": f"Missing required field: {field}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    try:
        saler_car = saler_car_details.objects.get(
            saler_car_id=data["saler_car_id"], user=user
        )
    except saler_car_details.DoesNotExist:
        return Response(
            {"message": "Car not found or unauthorized"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        availability = Availability.objects.get(id=data["availability_id"])
    except Availability.DoesNotExist:
        return Response(
            {"message": "Availability not found"}, status=status.HTTP_404_NOT_FOUND
        )

    selected_time_slot = data["time_slot"]
    if selected_time_slot not in availability.time_slots:
        return Response(
            {"message": "Selected time slot is not available"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if SelectedSlot.objects.filter(
        inspector=availability.inspector,
        date=availability.date,
        time_slot=selected_time_slot,
    ).exists():
        return Response(
            {"message": "Time slot already booked"}, status=status.HTTP_400_BAD_REQUEST
        )
    selected_slot = SelectedSlot(
        saler_car=saler_car,
        inspector=availability.inspector,
        date=availability.date,
        time_slot=selected_time_slot,
        booked_by="By Seller",
    )
    selected_slot.save()
    availability.time_slots = [
        slot for slot in availability.time_slots if slot != selected_time_slot
    ]
    availability.save()

    notification_message = f"Appointment scheduled for {saler_car.car_name} at {selected_time_slot} on {availability.date}"
    Notification.objects.create(
        recipient=availability.inspector,
        message=notification_message,
        category="seller_time_slot_selection",
    )
    return Response(
        {"message": "Time slot selected successfully"}, status=status.HTTP_201_CREATED
    )


# additional name and number post view
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def post_additional_details(request):
    serializer = AdditionalDetailSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"Message": "Data saved", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# list of saler cars
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_cars(request):
    user = request.user

    cars = saler_car_details.objects.filter(user=user).select_related("user")

    if not cars.exists():
        return Response(
            {"error": "No cars found for this user."},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = SalerCarDetailsSerializer(cars, many=True)

    return Response({"cars": serializer.data}, status=status.HTTP_200_OK)


# notifciation of appointment


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_appointment_notification(request):

    user = request.user

    notifications = Notification.objects.filter(
        recepient=user, category="inspector_gives_appointment"
    ).order_by("-created_at")

    serializer = NotificationSerializer(notifications, many=True)
    return Response(
        {"message": "Appointment", "notification": serializer.data},
        status=status.HTTP_200_OK,
    )


# SALER UPDATED CAR DETAILS
@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_car_details(request, car_id):
    user = request.user

    if user.role != "saler":
        return Response("only Sler can update", status=status.HTTP_400_BAD_REQUEST)

    try:
        saler_car = saler_car_details.objects.get(saler_car_id=car_id, user=user)
    except saler_car_details.DoesNotExist:
        return Response("Car not found", status=status.HTTP_404_NOT_FOUND)

    saler_phone_number = user.phone_number

    old_car_details = saler_car.__dict__.copy()

    serializer = SalerCarDetailsSerializer(saler_car, data=request.data, partial=True)

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

        return Response(
            {"message": "Updated successfully", "result": serializer.data},
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def saler_appointmet(request):
    user = request.user

    # Check if the user is a Seller
    if user.role != "saler":
        return Response(
            {"message": "Only sellers can view their appointments"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Fetch all appointments related to the seller
    appointments = saler_car_details.objects.filter(user=user).order_by(
        "inspection_date", "inspection_time"
    )

    if not appointments.exists():
        return Response(
            {"message": "No appointments found for this seller"},
            status=status.HTTP_404_NOT_FOUND,
        )

    serialized_appointments = SalerCarDetailsSerializer(appointments, many=True).data

    # Simplify the format for inspection date/time
    for i, appointment in enumerate(appointments):
        serialized_appointments[i]["inspection_date"] = (
            appointment.inspection_date.strftime("%Y-%m-%d")
        )
        serialized_appointments[i]["inspection_time"] = (
            appointment.inspection_time
        )

    return Response(
        {
            "message": "Seller appointments retrieved successfully",
            "appointments": serialized_appointments,
        },
        status=status.HTTP_200_OK,
    )


# Saler appointment Slot assigned by insppector manually


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def saler_manual_entry(request):
    user = request.user
    print("user appointmnt:", user)

    if user.role != "saler":
        return Response(
            {"Message": "Only Saler can view their appointments"},
            status=status.HTTP_403_FORBIDDEN,
        )

    appointments = AssignSlot.objects.filter(car__user=user).select_related(
        "car", "inspector"
    )

    appointments_data = []

    for appointment in appointments:
        appointment_datetime = timezone.make_aware(
            datetime.combine(appointment.date, appointment.time_slot)
        )
        appointments_data.append(
            {
                "appointment_id": appointment.id,
                "car_id": appointment.car.saler_car_id,
                "car_name": appointment.car.car_name,
                "company": appointment.car.company,
                "car_year": appointment.car.model,
                "is_inspected": appointment.car.is_inspected,
                "appointment_date": appointment.date.strftime("%Y-%m-%d"),
                "car_photos": appointment.car.photos,
                "appointment_time": appointment.time_slot.strftime("%H:%M"),
                "inspector_first_name": appointment.inspector.first_name,
                "inspector_last_name": appointment.inspector.last_name,
                "inspector_phone_number": appointment.inspector.phone_number,
                "inspector_adress": appointment.inspector.adress,
                "inspector_email": appointment.inspector.email,
                "status": appointment.car.status,
                "assigned_by": appointment.assigned_by,
                "created_at": appointment.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
    return Response({"appointments": appointments_data}, status=status.HTTP_200_OK)


# Saler update its details NOT USED NOW
@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def saler_update(request):
    user = request.user
    if user.role != "saler":
        return Response(
            {"message": "Only salers can update their details"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    data = request.data
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
        return Response(
            {
                "message": "User updated successfully",
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone_number": user.phone_number,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response(
            {"message": f"Error updating user: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )


# user delete its profile NOT USED NOW
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_saler(request):
    user = request.user

    if user.role != "saler":
        return Response(
            {"Message": "saler can delete its data"}, status=status.HTTP_400_BAD_REQUEST
        )

    if request.user.id != user.id:
        return Response(
            {"Message": "You can delete only your data"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user_id = user.id
        user.delete()

        return Response(
            {
                "message": f"User witg ID {user_id} delete successfully",
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# saler registeR view
# saler_register view
@api_view(["POST"])
@permission_classes([AllowAny])
def saler_register(request):
    data = request.data

    try:
        # Create the new user
        user = User.objects.create_user(
            username=data.get("username"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            email=data.get("email"),
            password=data.get("password"),
            phone_number=data.get("phone_number"),
            role="saler",
        )

        # Migrate any guest-related data to this new user
        # migrate_guest_to_user(
        #     guest_email=user.email,
        #     guest_number=user.phone_number,
        #     new_user=user
        # )

        return Response(
            {
                "message": "User created successfully",
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "email": user.email,
                "phone_number": user.phone_number,
                "role": user.role,
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# dealer register


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def dealer_register(request):

    if request.user.role != "admin":
        return Response(
            {"message": "Only admin can register a dealer."},
            status=status.HTTP_403_FORBIDDEN,
        )

    data = request.data

    try:
        user = User.objects.create_user(
            username=data.get("username"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            email=data.get("email"),
            password=data.get("password"),
            phone_number=data.get("phone_number"),
            adress=data.get("adress"),
            role="dealer",
        )

        return Response(
            {
                "message": "Dealer created successfully",
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "email": user.email,
                "phone_number": user.phone_number,
                "role": user.role,
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# update dealer
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def dealer_update(request, dealer_id):
    if request.user.role != "admin":
        return Response(
            {"message": "Only admin can update dealer details."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        user = User.objects.get(id=dealer_id, role="dealer")
    except User.DoesNotExist:
        return Response(
            {"message": "Dealer not found."}, status=status.HTTP_404_NOT_FOUND
        )

    data = request.data

    # Update fields if provided
    user.username = data.get("username", user.username)
    user.first_name = data.get("first_name", user.first_name)
    user.last_name = data.get("last_name", user.last_name)
    user.email = data.get("email", user.email)
    user.phone_number = data.get("phone_number", user.phone_number)
    user.adress = data.get("adress", user.adress)
    if data.get("password"):
        user.set_password(data["password"])

    user.save()

    return Response(
        {
            "message": "Dealer updated successfully",
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "email": user.email,
            "phone_number": user.phone_number,
            "role": user.role,
        },
        status=status.HTTP_200_OK,
    )


# inspector register
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def inspector_register(request):

    if request.user.role != "admin":
        return Response(
            {"message": "Only admin can register a dealer."},
            status=status.HTTP_403_FORBIDDEN,
        )

    data = request.data

    try:
        user = User.objects.create_user(
            username=data.get("username"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            email=data.get("email"),
            password=data.get("password"),
            phone_number=data.get("phone_number"),
            adress=data.get("adress"),
            role="inspector",
        )

        return Response(
            {
                "message": "inspector created successfully",
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "email": user.email,
                "phone_number": user.phone_number,
                "role": user.role,
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# update inspector
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def inspector_update(request, inspector_id):
    if request.user.role != "admin":
        return Response(
            {"message": "Only admin can update dealer details."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        user = User.objects.get(id=inspector_id, role="inspector")
    except User.DoesNotExist:
        return Response(
            {"message": "Dealer not found."}, status=status.HTTP_404_NOT_FOUND
        )

    data = request.data

    # Update fields if provided
    user.username = data.get("username", user.username)
    user.first_name = data.get("first_name", user.first_name)
    user.last_name = data.get("last_name", user.last_name)
    user.email = data.get("email", user.email)
    user.phone_number = data.get("phone_number", user.phone_number)
    user.adress = data.get("adress", user.adress)
    if data.get("password"):
        user.set_password(data["password"])

    user.save()

    return Response(
        {
            "message": "inspector updated successfully",
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "email": user.email,
            "phone_number": user.phone_number,
            "adress": user.adress,
            "role": user.role,
        },
        status=status.HTTP_200_OK,
    )


# admin register
@api_view(["POST"])
@permission_classes([AllowAny])
def admin_register(request):

    # if request.user.role != "admin":
    #     return Response({"message": "Only admin can register a dealer."},
    #                     status=status.HTTP_403_FORBIDDEN)

    data = request.data

    try:
        user = User.objects.create_user(
            username=data.get("username"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            email=data.get("email"),
            password=data.get("password"),
            phone_number=data.get("phone_number"),
            adress=data.get("adress"),
            role="admin",
        )

        return Response(
            {
                "message": "admin created successfully",
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "email": user.email,
                "phone_number": user.phone_number,
                "adress": user.adress,
                "role": user.role,
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# admin dealer
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def admin_update(request, admin_id):
    if request.user.role != "admin":
        return Response(
            {"message": "Only admin can update dealer details."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        user = User.objects.get(id=admin_id, role="admin")
    except User.DoesNotExist:
        return Response(
            {"message": "Admin not found."}, status=status.HTTP_404_NOT_FOUND
        )

    data = request.data

    # Update fields if provided
    user.username = data.get("username", user.username)
    user.first_name = data.get("first_name", user.first_name)
    user.last_name = data.get("last_name", user.last_name)
    user.email = data.get("email", user.email)
    user.phone_number = data.get("phone_number", user.phone_number)
    user.adress = data.get("adress", user.adress)
    if data.get("password"):
        user.set_password(data["password"])

    user.save()

    return Response(
        {
            "message": "admin updated successfully",
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "email": user.email,
            "phone_number": user.phone_number,
            "role": user.role,
        },
        status=status.HTTP_200_OK,
    )


# VIEW BIDS FOR SPECEFIC CAR
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def view_car_bids(request, car_id):
    try:
        car = saler_car_details.objects.get(saler_car_id=car_id)
    except saler_car_details.DoesNotExist:
        return Response({"Message": "car Not found"}, status=status.HTTP_404_NOT_FOUND)

    bids = Bidding.objects.filter(saler_car=car).order_by("-bid_date")

    serializer = BiddingSerializer(bids, many=True)

    return Response(
        {"Message": "Bids Fetched Successgully", "bids": serializer.data},
        status=status.HTTP_200_OK,
    )


# SELLER DELETE ITS CAR
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_ad(request, car_id):
    user = request.user
    print("user requesting for delete:", user)

    try:
        car = saler_car_details.objects.get(saler_car_id=car_id)
    except saler_car_details.DoesNotExist:
        return Response({"message": "car not found"}, status=status.HTTP_404_NOT_FOUND)

    if car.user != user:
        print("car owner:", car.user)
        return Response(
            {"message": "Unauthentecated"}, status=status.HTTP_403_FORBIDDEN
        )

    car.delete()

    return Response({"message": "car deleted successfully"}, status=status.HTTP_200_OK)


# SELLER UPDATED ITS CAR DETAIL


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_ad(request, car_id):
    user = request.user
    data = request.data

    try:
        car = saler_car_details.objects.get(saler_car_id=car_id)
    except saler_car_details.DoesNotExist:
        return Response({"message": "car not found"}, status=status.HTTP_404_NOT_FOUND)

    if car.user != user:
        return Response({"message": "UnAuthorized"}, status=status.HTTP_403_FORBIDDEN)

    serializer = SalerCarDetailsSerializer(car, data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "car updated successfully", "car": serializer.data},
            status=status.HTTP_200_OK,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Assign inspector to a car (Guest or Seller) ON CALL


@api_view(["POST"])
@permission_classes([AllowAny])
def assign_inspector_to_car(request):
    try:
        print("Incoming request data:", request.data)

        car_id = request.data.get("car_id")
        inspector_id = request.data.get("inspector_id")

        if not car_id or not inspector_id:
            return Response(
                {"error": "Car ID and Inspector ID are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            inspector = User.objects.get(id=inspector_id, role="inspector")
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid inspector selected"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            car = saler_car_details.objects.get(saler_car_id=car_id)
        except saler_car_details.DoesNotExist:
            return Response(
                {"error": "Car not found"}, status=status.HTTP_404_NOT_FOUND
            )

        car.inspector = inspector
        car.save()

        return Response(
            {"message": "Inspector assigned successfully!"}, status=status.HTTP_200_OK
        )

    except Exception as e:
        print(f"Error in assign_inspector_to_car: {e}")
        return Response(
            {"success": False, "message": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# GET THE CAR DETAILS OF SALER


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_car_details(request):
    user = request.user

    cars = saler_car_details.objects.filter(user=user)
    if not cars.exists():
        return Response(
            {"detail": "No car details found for this user."},
            status=status.HTTP_404_NOT_FOUND,
        )
    serializer = SalerCarDetailsSerializer(cars, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# lIST OF INSPECTORS


@api_view(["GET"])
@permission_classes([AllowAny])
def get_inspectors(request):
    try:
        inspector = User.objects.filter(role="inspector")
        serializer = UserSerializer(inspector, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# NOT USED
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_list_of_car_for_inspection(request):
    try:
        all_cars = saler_car_details.objects.all()

        serializer = SalerCarDetailsSerializer(all_cars, many=True)

        total_cars = all_cars.count()

        today = now().date()

        cars_today = all_cars.filter(created_at__date=today).count()

        all_cars_progress = 0
        if total_cars > 0:
            all_cars_progress = (cars_today / total_cars) * 100

        response_data = {
            "total_cars": total_cars,
            "cars_today": cars_today,
            "all_cars_progress": round(
                all_cars_progress, 2
            ),  # Round to 2 decimal places
            "cars": serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Error in get_list_of_car_for_inspection: {str(e)}")
        return Response(
            {"error": "An error occurred while fetching the car list."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# get the last car details only NOT USED
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_last_car_details(request):
    user = request.user

    last_car = (
        saler_car_details.objects.filter(user=user).order_by("-saler_car_id").first()
    )
    if not last_car:
        return Response(
            {"detail": "No car details found for this user."},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = SalerCarDetailsSerializer(last_car)
    return Response(serializer.data, status=status.HTTP_200_OK)


# GETTING & POSTING THE PHOTOS OF SALER CAR not used POST WITH CAR DETAILS
# @api_view(["POST", "GET"])
# @permission_classes([IsAuthenticated])
# def salerCarPhoto(request):
#     if request.method == "POST":
#         data = request.data
#         serializer = CarPhotoSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     elif request.method == "GET":
#         car_id = request.query_params.get("car", None)

#         if car_id:
#             car_photos = CarPhoto.objects.filter(car=car_id)
#         else:
#             car_photos = CarPhoto.objects.all()
#         serializer = CarPhotoSerializer(car_photos, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

# ///////////////////////////////INSPECTOR APIs////////////////////////////////


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def inspector_appointments(request):
    """Fetch all appointments for an inspector using serializers."""
    user = request.user

    if user.role != "inspector":
        return Response(
            {"message": "Only inspectors can view this data"},
            status=status.HTTP_403_FORBIDDEN,
        )

    appointments = saler_car_details.objects.filter(
        inspector=user, user__isnull=False, is_manual=False
    ).order_by("inspection_date", "inspection_time")

    if not appointments.exists():
        return Response(
            {"message": "No valid appointments found for this inspector"},
            status=status.HTTP_404_NOT_FOUND,
        )

    serialized_appointments = SalerCarDetailsSerializer(appointments, many=True).data

    # Optionally attach only inspection date/time in a simplified format
    for i, appointment in enumerate(appointments):
        serialized_appointments[i]["inspection_date"] = (
            appointment.inspection_date.strftime("%Y-%m-%d")
        )
        serialized_appointments[i]["inspection_time"] = (
            appointment.inspection_time
        )

    return Response(
        {
            "message": "Inspector appointments retrieved successfully",
            "appointments": serialized_appointments,
        },
        status=status.HTTP_200_OK,
    )


# INSPECTOR ASSIGN SLOTS


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def assign_slot(request):

    if "car_id" not in request.data:
        return Response(
            {"error": "Car ID is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    data = request.data.copy()
    data["inspector_id"] = request.user.id

    try:
        car = saler_car_details.objects.get(saler_car_id=data["car_id"])
    except saler_car_details.DoesNotExist:
        return Response({"error": "Invalid Car ID"}, status=status.HTTP_400_BAD_REQUEST)

    data["car"] = car.saler_car_id

    serializer = AssignedSlotSerializer(data=data, context={"request": request})

    if serializer.is_valid():
        assigned_slot = serializer.save()

        assigned_slot.time_slot = assigned_slot.time_slot.strftime("%H:%M")
        assigned_slot.save(update_fields=["time_slot"])
        try:
            availability = Availability.objects.get(
                inspector=assigned_slot.inspector, date=assigned_slot.date
            )
            availability.time_slots = [
                slot.strftime("%H:%M") if isinstance(slot, datetime) else slot
                for slot in availability.time_slots
            ]
            if assigned_slot.time_slot in availability.time_slots:
                availability.time_slots.remove(assigned_slot.time_slot)
                availability.save(update_fields=["time_slots"])

        except Availability.DoesNotExist:
            return Response(
                {"error": "Availability record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            AssignedSlotSerializer(assigned_slot).data, status=status.HTTP_201_CREATED
        )
    else:
        print("Errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# MANUAL APPOINTMENT
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_assigned_slots(request):
    assigned_slots = (
        AssignSlot.objects.select_related("car", "car__user", "inspector")
        .filter(
            Q(car__user__isnull=False)
            | Q(car__is_manual=True)
            | Q(car__guest__isnull=False)
        )
        .exclude(car__isnull=True)
    )

    serializer = AssignedSlotSerializer(assigned_slots, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# INSPECTOR POST INSPECTION REPORT
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def post_inspection_report(request):
    user = request.user
    if user.role != "inspector":
        return Response(
            {"message": "Only inspectors can submit inspection reports."},
            status=status.HTTP_403_FORBIDDEN,
        )

    data = request.data
    print("Inspection report data received:", data)

    # Get the saler_car ID from request
    saler_car_id = data.get("saler_car")
    if not saler_car_id:
        return Response(
            {"message": "Missing 'saler_car' field in request."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        car = saler_car_details.objects.get(saler_car_id=saler_car_id)
    except saler_car_details.DoesNotExist:
        return Response(
            {"message": "Car not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Prepare data for serializer
    serializer = InspectionReportSerializer(data=data)
    if serializer.is_valid():
        report = serializer.save(inspector=user, saler_car=car)

        # Notify Seller
        Notification.objects.create(
            recipient=car.user,
            message=f"Your car '{car.car_name} ({car.year})' has been inspected by {user.username}.",
            category="Your_car_inspected",
            saler_car=car,
        )

        # Notify Dealers
        dealers = User.objects.filter(role="dealer")
        for dealer in dealers:
            Notification.objects.create(
                recipient=dealer,
                message=f"The car '{car.car_name} ({car.year})' has been inspected. Check the inspection report.",
                category="dealer_car_inspected",
                saler_car=car,
            )

        # Notify Admins
        admins = User.objects.filter(role="admin")
        for admin in admins:
            Notification.objects.create(
                recipient=admin,
                message=f"The car '{car.car_name} ({car.year})' has been inspected. The inspection report is available.",
                category="admin_car_inspected",
                saler_car=car,
            )

        return Response(
            {
                "message": "Inspection report submitted successfully.",
                "report": InspectionReportSerializer(report).data,
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# INSPECTOR POST INSPECTION REPORT mobile
# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def post_inspection_report_mob(request):

#     user = request.user
#     if user.role != "inspector":
#         return Response(
#             {"message": "Only inspectors can submit inspection reports."},
#             status=status.HTTP_403_FORBIDDEN,
#         )

#     data = request.data
#     print("Inspection report data received From mobile app:", data)

#     # Get the saler_car ID from request
#     saler_car_id = data.get("saler_car")
#     if not saler_car_id:
#         return Response(
#             {"message": "Missing 'saler_car' field in request."},
#             status=status.HTTP_400_BAD_REQUEST,
#         )

#     try:
#         car = saler_car_details.objects.get(saler_car_id=saler_car_id)
#     except saler_car_details.DoesNotExist:
#         return Response(
#             {"message": "Car not found."},
#             status=status.HTTP_404_NOT_FOUND,
#         )
#   # "json_obj"
#     # Prepare the JSON data in the expected format
#     json_obj = data.get("json_obj")
#     mobile_data = {
#         "bodyParts": json_obj.get("bodyParts"),
#         # Add other sections from mobile data as needed
#     }

#     merge_result = merge_json(my_default_json, mobile_data)

#     # Create a copy of the data with the properly formatted json_obj
#     serializer_data = {
#         **data,
#         "json_obj": merge_result
#     }

#     serializer = InspectionReportSerializer(data=serializer_data)
#     if serializer.is_valid():
#         report = serializer.save(inspector=user, saler_car=car)

#         # Notify Seller
#         Notification.objects.create(
#             recipient=car.user,
#             message=f"Your car '{car.car_name} ({car.year})' has been inspected by {user.username}.",
#             category="Your_car_inspected",
#             saler_car=car,
#         )

#         # Notify Dealers and Admins (keep your existing code)
#         # ...

#         return Response(
#             {
#                 "message": "Inspection report submitted successfully.",
#                 "report": InspectionReportSerializer(report).data,
#             },
#             status=status.HTTP_201_CREATED,
#         )

#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def post_inspection_report_mob(request):
    user = request.user
    if user.role != "inspector":
        return Response(
            {"message": "Only inspectors can submit inspection reports."},
            status=status.HTTP_403_FORBIDDEN,
        )
    data = request.data
    print("Inspection report data received From mobile app:", data)
    # Get the saler_car ID from request
    saler_car_id = data.get("saler_car")
    if not saler_car_id:
        return Response(
            {"message": "Missing 'saler_car' field in request."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        car = saler_car_details.objects.get(saler_car_id=saler_car_id)
    except saler_car_details.DoesNotExist:
        return Response(
            {"message": "Car not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    # "json_obj"
    # Prepare the JSON data in the expected format
    json_obj = data.get("json_obj")
    mobile_data = {
        "basicInfo": json_obj.get("basicInfo", {}),
        "techSpecs": json_obj.get("techSpecs", {}),
        "bodyParts": json_obj.get("bodyParts", []),
    }
    merge_result = merge_json(my_default_json, mobile_data)
    # complete_josn = add_jsons(json.dumps(basic_json), json.dumps(merge_json))
    # Create a copy of the data with the properly formatted json_obj
    serializer_data = {**data, "json_obj": merge_result}
    serializer = InspectionReportSerializer(data=serializer_data)
    if serializer.is_valid():
        report = serializer.save(inspector=user, saler_car=car)
        # Notify Seller
        Notification.objects.create(
            recipient=car.user,
            message=f"Your car '{car.car_name} ({car.year})' has been inspected by {user.username}.",
            category="Your_car_inspected",
            saler_car=car,
        )
        # Notify Dealer
        Notification.objects.create(
            recipient=car.user,
            message=f"car '{car.car_name} ({car.year})' has been inspected by {user.username}.",
            category="dealer_car_inspected",
            saler_car=car,
        )
        Notification.objects.create(
            recipient=car.user,
            message=f"car '{car.car_name} ({car.year})' has been inspected by {user.username}.",
            category="admin_car_inspected",
            saler_car=car,
        )
        return Response(
            {
                "message": "Inspection report submitted successfully.",
                "report": InspectionReportSerializer(report).data,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# UPDATE INSPECTION REPORT


@permission_classes([IsAuthenticated])
@api_view(["PUT"])
def update_inspection_report(request, report_id):
    user = request.user
    if user.role != "inspector":
        return Response(
            {"message": "only inspector can update"}, status=status.HTTP_403_FORBIDDEN
        )

    try:
        report = InspectionReport.objects.get(id=report_id, inspector=user)
        print(f"Report found: {report}")
    except InspectionReport.DoesNotExist:
        # Debugging line
        print(f"Report with ID {report_id} not found for inspector {user}")
        return Response(
            {"message": "Report not found"}, status=status.HTTP_404_NOT_FOUND
        )

    data = request.data

    car_photos = data.get("car_photos", [])
    decoded_photos = []
    for index, photo in enumerate(car_photos):
        try:
            format, imgstr = photo.split(";base64,")
            ext = format.split("/")[-1]
            decoded_photos.append(f"data:image/{ext};base64,{imgstr}")
        except Exception as e:
            return Response(
                {"message": f"Error processing image: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    # Update fields
    report.car_name = data.get("car_name", report.car_name)
    report.company = data.get("company", report.company)
    report.color = data.get("color", report.color)
    report.condition = data.get("condition", report.condition)
    report.model = data.get("model", report.model)
    report.fuel_type = data.get("fuel_type", report.fuel_type)
    # report.registry_number = data.get("registry_number", report.registry_number)
    report.year = data.get("year", report.year)
    report.engine_capacity = data.get("engine_capacity", report.engine_capacity)
    report.mileage = data.get("mileage", report.mileage)
    # report.chassis_number = data.get("chassis_number", report.chassis_number)
    report.engine_type = data.get("engine_type", report.engine_type)
    report.transmission_type = data.get("transmission_type", report.transmission_type)

    # Update condition fields
    report.engine_condition = data.get("engine_condition", report.engine_condition)
    report.body_condition = data.get("body_condition", report.body_condition)
    report.clutch_condition = data.get("clutch_condition", report.clutch_condition)
    report.steering_condition = data.get(
        "steering_condition", report.steering_condition
    )
    report.suspension_condition = data.get(
        "suspension_condition", report.suspension_condition
    )
    report.brakes_condition = data.get("brakes_condition", report.brakes_condition)
    report.ac_condition = data.get("ac_condition", report.ac_condition)
    report.tyres_condition = data.get("tyres_condition", report.tyres_condition)
    report.electrical_condition = data.get(
        "electrical_condition", report.electrical_condition
    )

    # Update financial details
    report.estimated_value = data.get("estimated_value", report.estimated_value)
    report.saler_demand = data.get("saler_demand", report.saler_demand)

    # Update additional comments & photos
    report.additional_comments = data.get(
        "additional_comments", report.additional_comments
    )
    report.car_photos = decoded_photos if decoded_photos else report.car_photos

    # Recalculate overall score (average of all condition fields)
    condition_fields = [
        report.engine_condition,
        report.body_condition,
        report.clutch_condition,
        report.steering_condition,
        report.suspension_condition,
        report.brakes_condition,
        report.ac_condition,
        report.electrical_condition,
        report.tyres_condition,
    ]
    report.overall_score = sum(condition_fields) / len(condition_fields)

    report.save()

    # Send Notifications
    try:
        if report.saler_car.user:
            Notification.objects.create(
                recipient=report.saler_car.user,
                message=f"Your car '{report.saler_car.car_name}' inspection report has been updated.",
                category="inspection_updated",
                saler_car=report.saler_car,
            )

        dealers = User.objects.filter(role="dealer")
        for dealer in dealers:
            Notification.objects.create(
                recipient=dealer,
                message=f"Updated inspection report available for '{report.saler_car.car_name}'.",
                category="dealer_inspection_updated",
                saler_car=report.saler_car,
            )

        admins = User.objects.filter(role="admin")
        for admin in admins:
            Notification.objects.create(
                recipient=admin,
                message=f"Inspection report updated for '{report.saler_car.car_name}'.",
                category="admin_inspection_updated",
                saler_car=report.saler_car,
            )

    except Exception as e:
        logger.error(f"Error while creating notifications: {str(e)}")

    serialized_report = InspectionReportSerializer(report)
    return Response(
        {
            "message": "Inspection report updated successfully",
            "report": serialized_report.data,
        },
        status=status.HTTP_200_OK,
    )


# INSPECTORS ADD TIME AND DATE MAKE SCHEDULE


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def add_availability(request):
#     user = request.user

#     if user.role.lower() != "inspector":
#         return Response(
#             {"message": "Only an inspector can add availability"}, status=403
#         )
#     data = request.data
#     date_slots = data.get("dateSlots")

#     if not date_slots or not isinstance(date_slots, list):
#         return Response(
#             {"message": "A list of date and slot pairs is required"}, status=400
#         )

#     for entry in date_slots:
#         date_str = entry.get("date")
#         slots = entry.get("slots")

#         # Debugging log
#         print(f"Processing entry -> Date: {date_str}, Slots: {slots}")

#         if not date_str or not slots:
#             return Response(
#                 {"message": "Each entry must have a valid date and slots"}, status=400
#             )

#         try:
#             current_date = datetime.strptime(date_str, "%Y-%m-%d").date()
#             # Debugging log
#             print(f"Parsed date (before conversion): {current_date}")
#         except ValueError:
#             return Response(
#                 {"message": "Invalid date format. Use YYYY-MM-DD"}, status=400
#             )

#         server_time = localtime(now()).date()

#         if current_date < server_time:
#             return Response({"message": "Cannot add slots for past dates"}, status=400)

#         valid_slots = set()
#         for slot in slots:
#             try:
#                 if "AM" in slot.upper() or "PM" in slot.upper():
#                     slot_time = datetime.strptime(slot, "%I:%M %p").time()
#                 else:
#                     slot_time = datetime.strptime(slot, "%H:%M").time()

#                 valid_slots.add(slot_time.strftime("%H:%M"))
#             except ValueError:
#                 return Response(
#                     {
#                         "message": f"Invalid time format: {slot}. Use HH:MM or 12-hour format (e.g., 2:30 PM)"
#                     },
#                     status=400,
#                 )

#         availability, created = Availability.objects.get_or_create(
#             inspector=user, date=current_date
#         )

#         existing_slots = (
#             set(availability.time_slots) if availability.time_slots else set()
#         )
#         updated_slots = list(existing_slots.union(valid_slots))

#         availability.time_slots = updated_slots
#         availability.save()

#     return Response({"message": "Availability slots added successfully"}, status=201)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_availability(request):
    user = request.user

    if user.role.lower() != "inspector":
        return Response(
            {"message": "Only an inspector can add availability."}, status=403
        )

    data = request.data
    date_slots = data.get("dateSlots")

    if not date_slots or not isinstance(date_slots, list):
        return Response(
            {"message": "A list of date and slot pairs is required."}, status=400
        )

    try:
        for entry in date_slots:
            date_str = entry.get("date")
            slots = entry.get("slots")

            if not date_str or not slots or not isinstance(slots, list):
                return Response(
                    {"message": "Each entry must have a valid 'date' and a list of 'slots'."}, status=400
                )

            try:
                current_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"message": f"Invalid date format: {date_str}. Use YYYY-MM-DD."}, status=400
                )

            if current_date < localtime(now()).date():
                return Response(
                    {"message": "Cannot add slots for past dates."}, status=400
                )

            valid_slots = set()
            for slot in slots:
                try:
                    # store 12 hrs foramt 
                    parsed_time = datetime.strptime(slot.strip(), "%I:%M %p")
                    formatted_slot = parsed_time.strftime("%I:%M %p")
                    valid_slots.add(formatted_slot)
                except ValueError:
                    return Response(
                        {
                            "message": f"Invalid time format: {slot}. Use 12-hour format (e.g., 2:30 PM)."
                        },
                        status=400,
                    )

            availability, _ = Availability.objects.get_or_create(
                inspector=user, date=current_date
            )

            existing_slots = set(availability.time_slots or [])
            updated_slots = list(existing_slots.union(valid_slots))

            availability.time_slots = sorted(updated_slots)
            availability.save()

        return Response(
            {"message": "Availability slots added successfully."}, status=201
        )

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return Response(
            {"message": "An unexpected error occurred. Please try again later."},
            status=500,
        )
# when seller select slot


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_seller_appointment_notification(request):
    user = request.user
    appointment_notifications = Notification.objects.filter(
        recipient=user, category="seller_time_slot_selection"
    ).order_by("-created_at")

    serializer = NotificationSerializer(appointment_notifications, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_free_slots(request):
    try:
        date = request.query_params.get("date", None)
        inspector_id = request.query_params.get("inspector", None)

        if not inspector_id:
            return Response(
                {"message": "Inspector ID is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        if date:
            try:
                date_obj = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"message": "Invalid date format. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            date_obj = None

        availability_queryset = Availability.objects.filter(inspector_id=inspector_id)
        if date_obj:
            availability_queryset = availability_queryset.filter(date=date_obj)

        if not availability_queryset.exists():
            return Response(
                {"message": "No availability records found for the given inspector and date."},
                status=status.HTTP_404_NOT_FOUND,
            )

        reserved_slots_queryset = SelectedSlot.objects.filter(inspector_id=inspector_id)
        if date_obj:
            reserved_slots_queryset = reserved_slots_queryset.filter(date=date_obj)

        car_inspections = saler_car_details.objects.filter(inspector__id=inspector_id)
        if date_obj:
            car_inspections = car_inspections.filter(inspection_date=date_obj)

        taken_slots = set()
        unique_reserved_slots = {}

        # SelectedSlot entries
        for slot in reserved_slots_queryset:
            time_str = slot.time_slot.strftime("%H:%M")
            taken_slots.add(time_str)

            key = (slot.date, slot.inspector, time_str)
            if key not in unique_reserved_slots:
                unique_reserved_slots[key] = {
                    "source": "manual",
                    "slot_id": slot.id,
                    "date": slot.date.strftime("%Y-%m-%d"),
                    "inspector": slot.inspector.username,
                    "time_slot": time_str,
                }

        for car in car_inspections:
            if car.inspection_time:
                time_str = car.inspection_time  # ✅ Already string like '10:30 AM'
                taken_slots.add(time_str)

                key = (car.inspection_date, car.inspector, time_str)
                if key not in unique_reserved_slots:
                    unique_reserved_slots[key] = {
                        "slot_id": car.saler_car_id,
                        "date": car.inspection_date.strftime("%Y-%m-%d"),
                        "inspector": car.inspector.username if car.inspector else "",
                        "time_slot": time_str,
                        "car_name": car.car_name,
                        "status": car.status,
                    }

        reserved_slots = list(unique_reserved_slots.values())

        free_slots = []
        for availability in availability_queryset:
            available_time_slots = availability.time_slots
            available_free_slots = [
                str(slot) for slot in available_time_slots if str(slot) not in taken_slots
            ]

            for slot in available_free_slots:
                free_slots.append(
                    {
                        "availability_id": availability.id,
                        "date": availability.date.strftime("%Y-%m-%d"),
                        "inspector": availability.inspector.username,
                        "time_slot": slot,
                    }
                )

        return Response(
            {
                "message": "Fetched slots successfully",
                "free_slots": free_slots,
                "reserved_slots": reserved_slots,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"message": f"An unexpected error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

# GET ALL SLOTS -----NOT USED
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_available_slot(request):
    date = request.query_params.get("date")
    inspector_id = request.query_params.get("inspector")
    filters = {}
    if date:
        filters["date"] = date
    if inspector_id:
        filters["inspector_id"] = inspector_id

    availabilites = Availability.objects.filter(**filters)
    serializer = AvailabilitySerializer(availabilites, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_notifications_as_read(request):
    user = request.user
    Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)
    return Response(
        {"message": "Notifications marked as read"}, status=status.HTTP_200_OK
    )


# GET SELECTED SLOT
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_selected_slots(request):
    user = request.user

    # Fetch all slots selected by the current user
    selected_slots = SelectedSlot.objects.filter(saler_car__user=user)

    # Serialize the data
    serialized_slots = SelectedSlotSerializer(selected_slots, many=True)

    return Response(
        {
            "message": "Fetched selected slots successfully",
            "slots": serialized_slots.data,
        },
        status=status.HTTP_200_OK,
    )


# INSPECTION REPORT NOTIFICATION
@api_view(["GET"])
@permission_classes([AllowAny])
def get_inspection_notifications(request):
    user = request.user

    # For Saler
    if user.role == "saler":
        notifications = Notification.objects.filter(
            recipient=user,
            category="Your_car_inspected",
            saler_car__user=user,
        )

    # For Dealer
    elif user.role == "dealer":
        notifications = Notification.objects.filter(
            recipient=user,
            category="dealer_car_inspected",
        )

    # For Admin
    elif user.role == "admin":
        notifications = Notification.objects.filter(
            recipient=user,
            category="admin_car_inspected",
        )

    else:
        return Response(
            {"message": "No notifications for this role"},
            status=status.HTTP_403_FORBIDDEN,
        )
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# GET INSPECTION REPORT
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_inspection_report(request):
    car_id = request.GET.get("car_id")
    if not car_id:
        return Response(
            {"message": "Provide Car ID"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        report = InspectionReport.objects.get(saler_car=car_id)
        serializer = InspectionReportSerializer(report)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except InspectionReport.DoesNotExist:
        return Response(
            {"message": "No report found for this car"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except MultipleObjectsReturned:  # type: ignore
        # Handle case where multiple reports exist (shouldn't happen)
        report = InspectionReport.objects.filter(saler_car=car_id).first()
        serializer = InspectionReportSerializer(report)
        return Response(serializer.data, status=status.HTTP_200_OK)


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def get_inspection_report(request):
#     car_id = request.GET.get("car_id")

#     if not car_id:
#         return Response(
#             {"message": "Provide Car ID"}, status=status.HTTP_400_BAD_REQUEST
#         )

#     reports = InspectionReport.objects.select_related("saler_car__user").filter(
#         saler_car=car_id
#     )

#     if not reports.exists():
#         return Response(
#             {"message": "No report found for this car"},
#             status=status.HTTP_404_NOT_FOUND,
#         )

#     serialized_reports = InspectionReportSerializer(reports, many=True)

#     return Response(serialized_reports.data, status=status.HTTP_200_OK)


# get list of guest cars to show to inspector
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_guest_car_details(request):
    try:
        inspector_id = request.GET.get("inspector_id")

        if not inspector_id:
            return Response(
                {"error": "Inspector ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            inspector = User.objects.get(id=inspector_id, role__iexact="Inspector")
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid inspector ID"}, status=status.HTTP_400_BAD_REQUEST
            )

        assigned_cars = saler_car_details.objects.filter(
            inspector=inspector, status="pending", added_by="guest"
        ).select_related("guest")

        serializer = SalerCarDetailsSerializer(assigned_cars, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Error in get_guest_car_details: {e}")
        return Response(
            {"success": False, "message": f"Error retrieving assigned cars: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# ///////////////////////////DEALERS APIs/////////////////////////


# bidding cars status for dealer and admin
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_bidding_cars(request):
    user = request.user

    if user.role not in ["dealer", "admin"]:
        return Response(
            {"message": "Only dealers or admins can view this"},
            status=status.HTTP_403_FORBIDDEN,
        )

    cars = saler_car_details.objects.select_related("user").filter(status="bidding")

    if not cars.exists():
        return Response(
            {"error": "No cars found in bidding status"},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = SalerCarDetailsSerializer(cars, many=True)

    return Response(
        {"message": "Cars fetched successfully", "cars": serializer.data},
        status=status.HTTP_200_OK,
    )


# get cars with status inspection for dealer and admin (upcoming)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_upcoming_cars(request):
    cars = saler_car_details.objects.filter(
        Q(status="pending") | Q(status="in_inspection")
    )
    # print(f"UPCOMING CARS : {len(cars)}")
    if not cars.exists():
        return Response(
            {"Message": "No Upcoming cars Found!"}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = SalerCarDetailsSerializer(cars, many=True)

    return Response({"cars": serializer.data}, status=status.HTTP_200_OK)

    # except Exception as e:
    #    return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# DEALERS CAN PLACE BID
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def place_bid(request):
    user = request.user

    if user.role != "dealer":
        return Response(
            {"message": "Only dealers can place bids"}, status=status.HTTP_403_FORBIDDEN
        )

    data = request.data
    try:
        saler_car = saler_car_details.objects.get(saler_car_id=data["saler_car"])
    except saler_car_details.DoesNotExist:
        return Response({"message": "Car not found"}, status=status.HTTP_404_NOT_FOUND)

    if saler_car.is_sold:
        return Response(
            {"message": "This car is already sold"}, status=status.HTTP_400_BAD_REQUEST
        )

    bid = Bidding.objects.create(
        dealer=user, saler_car=saler_car, bid_amount=data["bid_amount"]
    )
    User = get_user_model()
    admin_users = User.objects.filter(role="admin")
    for admin in admin_users:
        Notification.objects.create(
            recipient=admin,
            message=f"A new bid of {data['bid_amount']} has been placed on {saler_car.company} {saler_car.car_name}",
            saler_car=saler_car,
            category="new_bid",
            bid=bid,
        )

    serializer = BiddingSerializer(bid)
    return Response(
        {
            "message": "Bid placed successfully",
            "bid_id": bid.id,
            "bid": serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


# DEALER CAN VIEW THEIR OWN BIDS


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def view_dealer_bids(request):
    user = request.user

    if user.role != "dealer":
        return Response(
            {"Message": "Onlt dealer can view their Bids"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    bids = Bidding.objects.filter(dealer=user).order_by("-bid_date")
    serializer = BiddingSerializer(bids, many=True)

    return Response(
        {"Message": "successfuly fetched", "bids": serializer.data},
        status=status.HTTP_200_OK,
    )


# dealer inventory API
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dealer_inventory(request):
    user = request.user
    if user.role != "dealer":
        return Response(
            {"message": "unauthorized cannot access this resource"},
            status=status.HTTP_403_FORBIDDEN,
        )

    cars = saler_car_details.objects.filter(winner_dealer=user)

    serializer = SalerCarDetailsSerializer(cars, many=True)
    return Response(
        {"message": "success", "cars": serializer.data}, status=status.HTTP_200_OK
    )


# ///////////////////////////////////GUEST APIs////////////////////////////////////////////

# GUEST ADD ITS BASIC DETAILS


@api_view(["POST"])
@permission_classes([AllowAny])
def post_guest_details(request):
    serializer = GuestSerializer(data=request.data)
    print(request.data)

    if serializer.is_valid():
        guest = serializer.save()
        return Response(
            {"Message": "Data saved", "guest_id": guest.id, "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# GUEST POST CAR FOR SALE
# @api_view(["POST"])
# @permission_classes([AllowAny])
# def guest_add_car_details(request):
#     try:
#         data = request.data.copy()
#         data["added_by"] = "guest"

#         guest_id = data.get("guest_id")
#         if not guest_id:
#             return Response(
#                 {"error": "Guest ID is required."}, status=status.HTTP_400_BAD_REQUEST
#             )

#         try:
#             guest = Guest.objects.get(id=guest_id)
#         except Guest.DoesNotExist:
#             return Response(
#                 {"error": "Invalid Guest ID."}, status=status.HTTP_400_BAD_REQUEST
#             )

#         data.pop("guest_id", None)
#         serializer = SalerCarDetailsSerializer(data=data)
#         if serializer.is_valid():
#             car_details = serializer.save(guest=guest)

#             return Response(
#                 {
#                     "message": "Car added successfully!",
#                     "car_id": car_details.saler_car_id,
#                 },
#                 status=status.HTTP_201_CREATED,
#             )

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     except Exception as e:
#         print(f"Error in guest_add_car_details view: {str(e)}")
#         return Response(
#             {"success": False, "message": "An error occurred while adding car details"},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


@api_view(["POST"])
@permission_classes([AllowAny])
def guest_add_car_details(request):
    try:
        data = request.data.copy()
        data["added_by"] = "guest"

        guest_id = data.get("guest_id")
        inspector_id = data.get("inspector_id")  # <-- NEW

        if not guest_id:
            return Response(
                {"error": "Guest ID is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            guest = Guest.objects.get(id=guest_id)
        except Guest.DoesNotExist:
            return Response(
                {"error": "Invalid Guest ID."}, status=status.HTTP_400_BAD_REQUEST
            )

        inspector = None
        if inspector_id:
            try:
                inspector = User.objects.get(id=inspector_id, role="inspector")
            except User.DoesNotExist:
                return Response(
                    {"error": "Invalid Inspector ID."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Remove extra fields not in serializer
        data.pop("guest_id", None)
        data.pop("inspector_id", None)

        serializer = SalerCarDetailsSerializer(data=data)
        if serializer.is_valid():
            car_details = serializer.save(guest=guest, inspector=inspector)

            # Create notification for inspector
            if inspector:
                Notification.objects.create(
                    recipient=inspector,
                    message=f"You have been assigned to inspect the car '{car_details.car_name}' by guest user.",
                    saler_car=car_details,
                    category="inspection_assignment",
                )

            return Response(
                {
                    "message": "Car added successfully!",
                    "car_id": car_details.saler_car_id,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print(f"Error in guest_add_car_details view: {str(e)}")
        return Response(
            {"success": False, "message": "An error occurred while adding car details"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# ////////////////////////////////////////////////////////other like status updating///////////////
# saler posted car notifications get


@api_view(["GET"])
@permission_classes({IsAuthenticated})
def get_notifications(requet):
    user = requet.user

    notification = Notification.objects.filter(
        recipient=user, category="saler_car_details"
    )

    serializer = NotificationSerializer(notification, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


# about saler car


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_notification_as_read(request, notification_id):
    try:
        notification = Notification.objects.get(
            id=notification_id, recipient=request.user
        )
        notification.is_read = True
        notification.save()
        return Response({"message": "Notification marked as read"}, status=200)
    except Notification.DoesNotExist:
        return Response({"message": "Notification not found"}, status=404)


# fetch assign slots
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_assigned_slots(request):
    user = request.user

    if user.role == "inspector":
        slots = SelectedSlot.objects.filter(inspector=user)
    elif user.role == "saler":
        slots = SelectedSlot.objects.filter(saler_car__user=user)
    else:
        return Response(
            {"message": "Unauthorized role."}, status=status.HTTP_403_FORBIDDEN
        )

    # Serialize the slots
    serializer = SelectedSlotSerializer(slots, many=True)
    return Response(
        {
            "message": "Assigned slots fetched successfully.",
            "slots": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# saler_car_detail sets is_manual = True
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_is_manual(request, car_id):
    try:
        car = saler_car_details.objects.get(pk=car_id)
        car.is_manual = True
        car.save(update_fields=["is_manual"])
        return Response({"message": "updated"}, status=status.HTTP_201_CREATED)
    except saler_car_details.DoesNotExist:
        return Response({"message": "car not found"}, status=status.HTTP_404_NOT_FOUND)


# on selecting slot


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_is_booked(request, car_id):
    try:
        car = saler_car_details.objects.get(pk=car_id)
        car.is_booked = True
        car.save(update_fields=["is_booked"])
        return Response({"message": "updated"}, status=status.HTTP_201_CREATED)
    except saler_car_details.DoesNotExist:
        return Response({"message": "car not found"}, status=status.HTTP_404_NOT_FOUND)


# update the car status
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_status(request, car_id):
    try:
        car = saler_car_details.objects.get(saler_car_id=car_id)
        new_status = request.data.get("status")
        print("staus:", new_status)

        valid_status = dict(saler_car_details.STATUS_CHOICES).keys()
        if new_status not in valid_status:
            return Response(
                {"Error": "invalid Status"}, status=status.HTTP_400_BAD_REQUEST
            )
        car.status = new_status
        car.save()

        return Response(
            {"message": "Status updated successfully", "new status": car.status},
            status=status.HTTP_200_OK,
        )

    except saler_car_details.DoesNotExist:
        return Response({"Error": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


# get seller manual entries
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def seller_manual_entries(request):
    try:
        # Get inspector ID from request
        inspector_id = request.GET.get("inspector_id")

        if not inspector_id:
            return Response(
                {"error": "Inspector ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate that the user is an inspector
        try:
            inspector = User.objects.get(id=inspector_id, role__iexact="Inspector")
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid inspector ID"}, status=status.HTTP_400_BAD_REQUEST
            )

        linked_cars = saler_car_details.objects.filter(
            inspector=inspector,
            user__isnull=False,
            guest__isnull=True,
            status="pending",
        ).distinct()

        # Serialize the data
        serializer = SalerCarDetailsSerializer(linked_cars, many=True)
        return Response(
            {"success": True, "linked_cars": serializer.data}, status=status.HTTP_200_OK
        )

    except Exception as e:
        print(f"Error in seller_manual_entries: {e}")  # Debugging
        return Response(
            {"success": False, "message": f"Error retrieving linked cars: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# is_inspected true
@api_view(["POST"])
def mark_as_inspected(request, car_id):
    car = get_object_or_404(saler_car_details, saler_car_id=car_id)
    car.is_inspected = True
    car.save()
    return Response(
        {"message": "Car marked as inspected", "is_inspected": car.is_inspected}
    )

    # /////////////////////////////////////////////////////////////////////////////////////////////////


# for inspector whose date time selected
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def inspector_web_appointments(request):
#     inspector = request.user

#     cars = saler_car_details.objects.filter(inspector=inspector)

#     serializer = SalerCarDetailsSerializer(cars , many=True)

#     return Response(serializer.data ,status=status.HTTP_200_OK)

# web seller posted add
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def seller_posted_add(request):
#     user = request.user

#     cars = saler_car_details.objects.filter(user=user).order_by('created_at')

#     serializer = SalerCarDetailsSerializer(cars, many=True)

#     return Response(serializer.data, status=status.HTTP_200_OK)

# Get free and reserved slots for an inspector
# @api_view(["GET"])
# @permission_classes([AllowAny])
# def get_free_slots(request):
#     date = request.query_params.get("date", None)
#     inspector_id = request.query_params.get("inspector", None)

#     if not inspector_id:
#         return Response(
#             {"message": "Inspector ID is required."}, status=status.HTTP_400_BAD_REQUEST
#         )
#     if date:
#         try:
#             date_obj = datetime.strptime(date, "%Y-%m-%d").date()
#         except ValueError:
#             return Response(
#                 {"message": "Invalid date format. Use YYYY-MM-DD."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#     else:
#         date_obj = None
#     availability_queryset = Availability.objects.filter(inspector_id=inspector_id)
#     if date_obj:
#         availability_queryset = availability_queryset.filter(date=date_obj)

#     if not availability_queryset.exists():
#         return Response(
#             {
#                 "message": "No availability records found for the given inspector and date."
#             },
#             status=status.HTTP_404_NOT_FOUND,
#         )

#     # Fetch reserved slots
#     reserved_slots_queryset = SelectedSlot.objects.filter(inspector_id=inspector_id)
#     if date_obj:
#         reserved_slots_queryset = reserved_slots_queryset.filter(date=date_obj)

#     unique_reserved_slots = {}

#     for slot in reserved_slots_queryset:
#         key = (slot.date, slot.inspector, str(slot.time_slot)[:5])  # Unique identifier

#         if key not in unique_reserved_slots:
#             unique_reserved_slots[key] = {
#                 "slot_id": slot.id,
#                 "date": slot.date.strftime("%Y-%m-%d"),
#                 "inspector": slot.inspector.username,
#                 "time_slot": str(slot.time_slot)[:5],
#             }

#     reserved_slots = list(unique_reserved_slots.values())
#     taken_slots = set(
#         slot.time_slot.strftime("%H:%M") for slot in reserved_slots_queryset
#     )

#     # Fetch free slots
#     free_slots = []
#     for availability in availability_queryset:
#         available_time_slots = availability.time_slots
#         available_free_slots = [
#             str(slot) for slot in available_time_slots if str(slot) not in taken_slots
#         ]

#         for slot in available_free_slots:
#             free_slots.append(
#                 {
#                     "availability_id": availability.id,
#                     "date": availability.date.strftime("%Y-%m-%d"),
#                     "inspector": availability.inspector.username,
#                     "time_slot": slot,  # Already stored as HH:MM
#                 }
#             )

#     return Response(
#         {
#             "message": "Fetched slots successfully",
#             "free_slots": free_slots,
#             "reserved_slots": reserved_slots,
#         },
#         status=status.HTTP_200_OK,
#     )


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def post_inspection_report(request):
#     user = request.user
#     if user.role != "inspector":
#         return Response(
#             {"message": "Only inspectors can submit"},
#             status=status.HTTP_400_BAD_REQUEST,
#         )

#     data = request.data
#     print("Inspection report:", data)

#     # Safely get saler_car from request
#     saler_car = data.get("saler_car")
#     if not saler_car:
#         return Response(
#             {"message": "Missing 'saler_car' in request."},
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     try:
#         # Try to get the car based on the saler_car ID
#         car = saler_car_details.objects.get(saler_car_id=saler_car)
#     except saler_car_details.DoesNotExist:
#         return Response({"message": "Car not found"}, status=status.HTTP_404_NOT_FOUND)

#     # Decode base64 car photos if any
#     car_photos = data.get("car_photos", [])
#     decoded_photos = []
#     for index, photo in enumerate(car_photos):
#         try:
#             format, imgstr = photo.split(";base64,")
#             ext = format.split("/")[-1]
#             decoded_photos.append(f"data:image/{ext};base64,{imgstr}")
#         except Exception as e:
#             return Response(
#                 {"message": f"Error processing image: {str(e)}"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#     # Inject decoded photos into request data
#     mutable_data = request.data.copy()
#     mutable_data["car_photos"] = decoded_photos

#     # Use serializer to create the report
#     serializer = InspectionReportSerializer(data=mutable_data)
#     if serializer.is_valid():
#         report = serializer.save(inspector=user, saler_car=car)

#         # Send notifications to car owner, dealers, and admins
#         try:
#             if car.user:
#                 Notification.objects.create(
#                     recipient=car.user,
#                     message=f"Your car '{car.car_name} ({car.model})' has been inspected by {user.username}.",
#                     category="Your_car_inspected",
#                     saler_car=car,
#                 )
#                 logger.info(f"Notification sent to car owner: {car.user.username}")

#             dealers = User.objects.filter(role="dealer")
#             logger.info(f"Found {dealers.count()} dealers.")
#             for dealer in dealers:
#                 Notification.objects.create(
#                     recipient=dealer,
#                     message=f"The car '{car.car_name} ({car.model})' has been inspected. Check the inspection report.",
#                     category="dealer_car_inspected",
#                     saler_car=car,
#                 )

#             admins = User.objects.filter(role="admin")
#             logger.info(f"Found {admins.count()} admins.")
#             for admin in admins:
#                 Notification.objects.create(
#                     recipient=admin,
#                     message=f"The car '{car.car_name} ({car.model})' has been inspected. The inspection report is available.",
#                     category="admin_car_inspected",
#                     saler_car=car,
#                 )

#             logger.info("All notifications created successfully.")
#         except Exception as e:
#             logger.error(f"Error while creating notifications: {str(e)}")

#         return Response(
#             {
#                 "message": "Inspection report submitted successfully",
#                 "report": InspectionReportSerializer(report).data,
#             },
#             status=status.HTTP_201_CREATED,
#         )
#     else:
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# SALER SEE ONLY ITS APPOINTMENT WITH INSPECTOR Time selected by selller
# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def saler_appointmet(request):
#     user = request.user

#     if user.role != "saler":
#         return Response(
#             {"Message": "Only Saler can view their appointment"},
#             status=status.HTTP_403_FORBIDDEN,
#         )

#     # Fetch all appointments related to the seller
#     appointments = SelectedSlot.objects.filter(saler_car__user=user).select_related(
#         "saler_car", "inspector"
#     )

#     appointments_data = []

#     for appointment in appointments:
#         # Convert date & time to a timezone-aware datetime object
#         appointment_datetime = timezone.make_aware(
#             datetime.combine(appointment.date, appointment.time_slot)
#         )
#         remaining_seconds = (appointment_datetime - timezone.now()).total_seconds()
#         remaining_days = int(remaining_seconds // (24 * 3600))
#         remaining_hours = int(
#             (remaining_seconds % (24 * 3600)) // 3600
#         )
#         remaining_minutes = int(
#             (remaining_seconds % 3600) // 60
#         )
#         remaining_secs = int(remaining_seconds % 60)

#         # Append data to list
#         appointments_data.append(
#             {
#                 "appointment_id": appointment.id,
#                 "car_id":appointment.saler_car.saler_car_id,
#                 "car_name": appointment.saler_car.car_name,
#                 "company": appointment.saler_car.company,
#                 "car_year": appointment.saler_car.model,
#                 "is_inspected": appointment.saler_car.is_inspected,
#                 "appointment_date": appointment.date.strftime("%Y-%m-%d"),
#                 "car_photos": appointment.saler_car.photos,
#                 "appointment_time": appointment.time_slot.strftime("%H:%M"),
#                 "inspector_first_name": appointment.inspector.first_name,
#                 "inspector_last_name": appointment.inspector.last_name,
#                 "inspector_phone_number": appointment.inspector.phone_number,
#                 "inspector_adress": appointment.inspector.adress,
#                 "inspector_email": appointment.inspector.email,
#                 "remaining_days": remaining_days,
#                 "remaining_hours": remaining_hours,
#                 "remaining_minutes": remaining_minutes,
#                 "remaining_seconds": remaining_secs,
#             }
#         )


#     return Response({"appointments": appointments_data}, status=status.HTTP_200_OK)


# INSPECTOR CAN SEE ALL APPOINTMENTS
# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def inspector_appointments(request):
#     """Fetch all appointments for an inspector where the seller is not null."""
#     user = request.user

#     if user.role != "inspector":
#         return Response(
#             {"message": "Only inspectors can view this data"},
#             status=status.HTTP_403_FORBIDDEN,
#         )
#     appointments = (
#         SelectedSlot.objects.filter(inspector=user)
#         .filter(
#             Q(saler_car__user__isnull=False)
#             & Q(saler_car__is_manual=False)
#         )
#         .order_by("date", "time_slot")
#     )
#     if not appointments.exists():
#         return Response(
#             {"message": "No valid appointments found for this inspector"},
#             status=status.HTTP_404_NOT_FOUND,
#         )

#     unique_appointments = {}
#     now = timezone.now()

#     for appointment in appointments:
#         car_id = appointment.saler_car.saler_car_id

#         if car_id not in unique_appointments:
#             appointment_datetime = datetime.combine(
#                 appointment.date, appointment.time_slot
#             )
#             if timezone.is_naive(appointment_datetime):
#                 appointment_datetime = timezone.make_aware(appointment_datetime)

#             remaining_seconds = max(
#                 0, int((appointment_datetime - now).total_seconds())
#             )
#             remaining_days = remaining_seconds // (24 * 3600)
#             remaining_hours = (remaining_seconds % (24 * 3600)) // 3600
#             remaining_minutes = (remaining_seconds % 3600) // 60
#             remaining_secs = remaining_seconds % 60

#             unique_appointments[car_id] = {
#                 "appointment_id": appointment.id,
#                 "car_id": car_id,
#                 "seller_first_name": (
#                     appointment.saler_car.user.first_name
#                     if appointment.saler_car.user
#                     else "N/A"
#                 ),
#                 "seller_last_name": (
#                     appointment.saler_car.user.last_name
#                     if appointment.saler_car.user
#                     else "N/A"
#                 ),
#                 "seller_phone_number": (
#                     appointment.saler_car.user.phone_number
#                     if appointment.saler_car.user
#                     else "N/A"
#                 ),
#                 "seller_email": (
#                     appointment.saler_car.user.email
#                     if appointment.saler_car.user
#                     else "N/A"
#                 ),
#                 "car_name": appointment.saler_car.car_name,
#                 "car_company": appointment.saler_car.company,
#                 "car_model": appointment.saler_car.model,
#                 "car_color": appointment.saler_car.color,
#                 "car_condition": appointment.saler_car.condition,
#                 "car_demand": appointment.saler_car.demand,
#                 "car_city": appointment.saler_car.city,
#                 "is_sold": appointment.saler_car.is_sold,
#                 "mileage": appointment.saler_car.milage,
#                 "description": appointment.saler_car.description,
#                 "type": appointment.saler_car.type,
#                 "fuel_type": appointment.saler_car.fuel_type,
#                 "registered_in": appointment.saler_car.registered_in,
#                 "assembly": appointment.saler_car.assembly,
#                 "engine_capacity": appointment.saler_car.engine_capacity,
#                 "photos": [
#                     (
#                         f"data:image/jpeg;base64,{photo}"
#                         if not photo.startswith("data:image")
#                         else photo
#                     )
#                     for photo in appointment.saler_car.photos
#                 ],
#                 "status": appointment.saler_car.status,
#                 "created_at": appointment.saler_car.created_at.strftime(
#                     "%Y-%m-%d %H:%M:%S"
#                 ),
#                 "updated_at": appointment.saler_car.updated_at.strftime(
#                     "%Y-%m-%d %H:%M:%S"
#                 ),
#                 "is_inspected": appointment.saler_car.is_inspected,
#                 "added_by": (
#                     appointment.saler_car.added_by
#                     if hasattr(appointment.saler_car, "added_by")
#                     else None
#                 ),
#                 "inspector": (
#                     appointment.inspector.id if appointment.inspector else None
#                 ),
#                 "date": appointment.date.strftime("%Y-%m-%d"),
#                 "time_slot": appointment.time_slot.strftime("%H:%M:%S"),
#                 "remaining_days": remaining_days,
#                 "remaining_hours": remaining_hours,
#                 "remaining_minutes": remaining_minutes,
#                 "remaining_seconds": remaining_secs,
#                 "selected_by": appointment.booked_by,
#             }

#     return Response(
#         {
#             "message": "Inspector appointments retrieved successfully",
#             "appointments": list(unique_appointments.values()),
#         },
#         status=status.HTTP_200_OK,
#     )
