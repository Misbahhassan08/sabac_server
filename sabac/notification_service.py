# # 
# from sabac.firebase_utils import send_fcm_notification
# from sabac.models import DeviceDetail


# def send_notification(title, body, role=None, user=None):
#     if user:
#         notifications = DeviceDetail.objects.filter(user=user, device_token__isnull=False)
#     elif role:
#        notifications = DeviceDetail.objects.filter(role=role, device_token__isnull=False)
#     else:
#         return []
# # 
#     results = []
#     for notif in notifications:
#         if user and notif.role == "seller" and notif.device_token:  
#             # send only if this notification belongs to this seller
#             status_code, response_text = send_fcm_notification(
#                 notif.device_token, notif.role, title, body
#             )
#             results.append({
#                 "device_token": notif.device_token,
#                 "role": notif.role,
#                 "fcm_status": status_code,
#                 "fcm_response": response_text,
#             })
#         elif not user:  # broadcast case
#             status_code, response_text = send_fcm_notification(
#                 notif.device_token, notif.role, title, body
#             )
#             results.append({
#                 "device_token": notif.device_token,
#                 "role": notif.role,
#                 "fcm_status": status_code,
#                 "fcm_response": response_text,
#             })
#     return results


# utils/notifications.py

from sabac.firebase_utils import send_fcm_notification


def send_notification(title, body, role=None, user=None,more_detail=None):
    from sabac.models import DeviceDetail
    """
    Send push notifications via FCM.
    - If `user` is provided, sends to that specific user's devices.
    - If `role` is provided, sends to all users with that role.
    """

    if user:
        notifications = DeviceDetail.objects.filter(user=user, device_token__isnull=False)
    elif role:
        notifications = DeviceDetail.objects.filter(role=role, device_token__isnull=False)
    else:
        return []

    results = []
    for notif in notifications:
        if notif.device_token:
            status_code, response_text = send_fcm_notification(
                notif.device_token, notif.role, title, body,more_detail=more_detail
            )
            results.append({
                "device_token": notif.device_token,
                "role": notif.role,
                "user_id": notif.user.id if notif.user else None,
                "fcm_status": status_code,
                "fcm_response": response_text,
            })

    return results
