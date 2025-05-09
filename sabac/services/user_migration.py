from django.db import transaction
from sabac.models import Guest, User, saler_car_details


@transaction.atomic
def migrate_guest_to_user(guest_email, guest_number, new_user):

    guest = Guest.objects.filter(
        email=guest_email, number=guest_number).first()

    if not guest:
        return
    saler_car_details.objects.filter(
        guest=guest).update(user=new_user, guest=None)

    guest.delete()
