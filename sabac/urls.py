
from django.urls import path
from .views import   get_free_slots , register , is_authentecated, salerCarPhoto, add_availability, select_slot, get_selected_slots, post_inspection_report, get_inspection_report, saler_register, add_car_details, get_car_details, get_notifications, get_inspection_notifications, get_cars_list, get_seller_appointment_notification, assign_slot, get_assigned_slots, get_appointment_notification,place_bid,view_car_bids,accept_bid,view_dealer_bids,update_car_details,saler_update,delete_saler,delete_user,edit_user,get_last_car_details,assign_inspector_to_car
from .views import get_list_of_car_for_inspection,get_inspectors,saler_appointmet,inspector_appointments,update_status,get_bidding_cars,get_upcoming_cars,approve_inspection,get_cars_for_approval,mark_bid_notifications_as_read,post_guest_details,get_bidding_cars_count
from .views import get_assigned_slots,mark_notifications_as_read,post_additional_details,get_user_cars,reject_inspection,bid_notification_for_seller,reject_bid,guest_add_car_details,get_guest_car_details,seller_manual_entries,assign_inspector_to_seller_car,get_highest_bid
urlpatterns = [

    path('register/', register , name='register'),   # for registring user
    path('authentecation/',is_authentecated),    # check authentecation
    path('saler_car_photos/',salerCarPhoto , name='car photos'),  # getting and post saler car photos 
    path('add_availability/',add_availability, name='add_availability'), #add availability url
    path('select_slot/',select_slot,name='select_slot'), #saler select slot
    path('get_selected_slots/',get_selected_slots,name='get_selected_slots'), #get selected slots
    path('get_free_slots/', get_free_slots, name='get_free_slots'), #get available slots
    path('post_inspection_report/',post_inspection_report,name='post_inspection_report'), #post inspection report
    path('get_inspection_report/',get_inspection_report,name='get_inspection_report'), #get inspection report of specefic car 
    path('saler_register/', saler_register, name='saler_register'), #url only saler can register by this
    path('add_car_details/',add_car_details, name='add_car_details'), # saler post saler car details
    path('get_car_details/',get_car_details,name='get_car_details'), #get saler car details
    path('notifications/', get_notifications, name='get_notifications'), #get notification
    path('inspection-notifications/', get_inspection_notifications, name='inspection_notifications'), #saler gets inspection notification
    path('get_cars_list/',get_cars_list,name='get_cars_list'), #list of all cars
    path('get_seller_appointment_notification/',get_seller_appointment_notification,name='get_seller_appointment_notification'), #seler select slot send notification to inspector
    # path('assign_slot/',assign_slot,name='assign_slot'), #inspector sets appointment
    # path('get_assigned_slots/',get_assigned_slots,name='get_assigned_slots'), #get assign slots
    path('get_appointment_notification/',get_appointment_notification,name='get_appointment_notification'), #when inspecor gives time to saler
    path('place_bid/',place_bid,name='place_bid'),#dealer posted bids
    path('view_car_bids/<int:car_id>/',view_car_bids,name='view_car_bids'), #bids on car
    path('accept_bid/<int:bid_id>/',accept_bid,name='accept_bid'), #saler accept bid
    path('reject_bid/<int:bid_id>/',reject_bid,name='accept_bid'), #saler reject bid
    path('view_dealer_bids/',view_dealer_bids,name='view_dealer_bids'), #dealer view own bids
    path('update_car_details/<int:car_id>/',update_car_details,name='update_car_details'), #slaer update its car details
    path('saler_update/',saler_update,name='saler_update'),#saler update own details
    path('delete_saler/',delete_saler,name='delete_saler'), #saler delete itself
    path('delete_user/',delete_user,name='delete_user'), #admin delete other user 
    path('edit_user/',edit_user,name='edit_user'), #admin edit user
    path('get_last_car_details/',get_last_car_details,name='get_last_car_details'), #for seller show its last car posted
    path('get_list_of_car_for_inspection/',get_list_of_car_for_inspection,name='get_list_of_car_for_inspection'),# list of all sellers cars for inspection
    path('get_inspectors/',get_inspectors,name='get_inspectors'), #list of inspectors 
    path('saler_appointmet/',saler_appointmet,name='saler_appointmet'), #seller view own appointment
    path('inspector_appointments/',inspector_appointments,name='inspector_appointments'), #inspector view appointments with sellers
    path("assign_slot/", assign_slot, name="assign-slot"), #inspector assign slot to seller
    path("get_assigned_slots/",get_assigned_slots,name="get_assign_slots"),
    path("mark_notifications_as_read/",mark_notifications_as_read,name='mark_notifications_as_read'),
    path("post_additional_details/",post_additional_details,name='post_additional_details'), #saler name and number for inspection
    path("get_user_cars/",get_user_cars,name="get_user_cars"), #list of saler cars on saler view
    path("update_status/<int:car_id>/",update_status,name="update_status"), #updated the status of car like pending ,bidding
    path("get_bidding_cars/",get_bidding_cars,name='get_bidding_cars'), #cars list with status bidding
    path("get_upcoming_cars/",get_upcoming_cars, name="get_upcoming_cars"), #upcoming cars status in_inspection for dealer
    path("approve_inspection/<int:report_id",approve_inspection,name="approve_inspection"), # admin inspection approving url
    path("reject_inspection/<int:car_id>",reject_inspection,name="reject_inspection"), #admin reject inspection
    path("get_cars_for_approval/",get_cars_for_approval,name="get_cars_for_approval"), #get cars for admin with await_approval
    path("Bid_notification_for_seller/",bid_notification_for_seller,name="bid_notification_for_seller"), #fetch bid notification for seller
    path("mark_bid_notifications_as_read/",mark_bid_notifications_as_read, name="mark_bid_notifications_as_read"),
    path("post_guest_details/",post_guest_details,name="post_guest_details"),
    path("guest_add_car_details/",guest_add_car_details , name="guest_add_car_details"),
    path("get_guest_car_details/",get_guest_car_details, name="get_guest_car_details"),
    path("assign_inspector_to_car/",assign_inspector_to_car,name="assign_inspector_to_car"),
    path("seller_manual_entries/",seller_manual_entries,name="seller_manual_entries"),
    path('assign-inspector-to-seller-car/', assign_inspector_to_seller_car, name='assign_inspector_to_seller_car'),
    path('get_bidding_cars_count/',get_bidding_cars_count,name="get_bidding_cars_count"),
    path('get_highest_bid/',get_highest_bid, name="get_highest_bid")

    

]   