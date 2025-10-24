import sys

from apscheduler.schedulers.background import BackgroundScheduler
from django.apps import AppConfig
from django.utils import timezone as dj_timezone


class SabacConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sabac"
    
    def ready(self):
        if "runserver" not in sys.argv:
            return

        from django.contrib.auth import get_user_model

        from .models import Guest, Notification, saler_car_details
        from .notification_service import send_notification  

        User = get_user_model()
        scheduler = BackgroundScheduler(timezone="Asia/Karachi")

        def expire_cars_job():
            now = dj_timezone.now()
      

            expired_sellers = saler_car_details.objects.filter(
                status="bidding", bidding_end_time__lt=now, is_sold=False
            )
   
            expired_guests = Guest.objects.filter(
                status="bidding", bidding_end_time__lt=now, is_sold=False
            )

            admins = User.objects.filter(role="admin")
            dealers = User.objects.filter(role="dealer")

            for car in expired_sellers:
                car.status = "expired"
                car.save(update_fields=["status"])
                car_info = f"{car.company} {car.car_name} {car.car_variant or ''}".strip()


                for admin in admins:
                    message = f"{car_info} has expired — no winning bid."
                    Notification.objects.create(
                        recipient=admin,
                        message=message,
                        saler_car=car,
                        category="admin_car_expired",
                    )
                    send_notification(
                        title="Car Expired",
                        body=message,
                        user=admin,
                        more_detail={
                            "car_type": "seller",
                            "car_id": str(car.saler_car_id),
                            "car_name": car.car_name,
                            "tab": "expire",
                        },
                    )


                for dealer in dealers:
                    message = f"The bidding period for {car_info} has ended."
                    Notification.objects.create(
                        recipient=dealer,
                        message=message,
                        saler_car=car,
                        category="dealer_car_expired",
                    )
                    send_notification(
                        title="Car Expired",
                        body=message,
                        user=dealer,
                        more_detail={
                            "car_type": "seller",
                            "car_id": str(car.saler_car_id),
                            "car_name": car.car_name,
                            "tab": "expire",
                        },
                    )

                # print(f"[✅ Auto-expired] Seller Car ID {car.saler_car_id} - {car_info}")

            for car in expired_guests:
                car.status = "expired"
                car.save(update_fields=["status"])
                car_info = f"{car.company} {car.car_name} {car.car_variant or ''}".strip()

                for admin in admins:
                    message = f"{car_info} (Guest Listing) has expired — no winning bid."
                    Notification.objects.create(
                        recipient=admin,
                        message=message,
                        guest_car=car,
                        category="admin_guest_expired",
                    )
                    send_notification(
                        title="Guest Car Expired",
                        body=message,
                        user=admin,
                        more_detail={
                            "car_type": "guest",
                            "car_id": str(car.id),
                            "car_name": car.car_name,
                            "tab": "expire",
                        },
                    )

                for dealer in dealers:
                    message = f"The bidding period for guest car {car_info} has ended."
                    Notification.objects.create(
                        recipient=dealer,
                        message=message,
                        guest_car=car, 
                        category="dealer_guest_expired",
                    )
                    send_notification(
                        title="Guest Car Expired",
                        body=message,
                        user=dealer,
                        more_detail={
                            "car_type": "guest",
                            "car_id": str(car.id),
                            "car_name": car.car_name,
                            "tab": "expire",
                        },
                    )

                # print(f"[✅ Auto-expired] Guest Car ID {car.id} - {car_info}")

            # print("✅ Expiry check completed.\n")


        scheduler.add_job(expire_cars_job, "interval", seconds=1, id="expire_cars_job", replace_existing=True)
        scheduler.start()
        # print("🚀 APScheduler started: Auto-expiring bidding cars every minute")
