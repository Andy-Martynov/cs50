from django.urls import path

from . import views

app_name = 'meeting'
urlpatterns = [
    path("", views.index, name="index"),

    path("map", views.map, name="map"),
    path("location", views.location, name="location"),

    path("stma", views.set_tags_markers_all, name="stma"),

    path("users_info", views.users_info, name="users_info"),
    path("locations_info/<int:user_id>", views.locations_info, name="locations_info"),

    path("user_info/<int:id>", views.user_info, name="user_info"),
    path("loc/<int:id>", views.location_info, name="location_info"),
    path("group_info/<int:id>", views.group_info, name="group_info"),
    path("meeting_info/<int:id>", views.meeting_info, name="meeting_info"),


    path("location_create", views.LocationCreate.as_view(), name="location_create"),
    path("location_create/<str:lat>/<str:lng>", views.LocationCreate.as_view(), name="location_create"),

    path("location_update/<int:pk>", views.LocationUpdate.as_view(), name="location_update"),
    path("location_delete/<int:location_id>", views.location_delete, name="location_delete"),

    path("location_list", views.LocationList.as_view(), name="location_list"),
    path("location_list/<int:owner_id>", views.LocationList.as_view(), name="location_list"),

    path("update_last_location", views.update_last_location, name="update_last_location"),
    path("resize_60x60/<int:id>", views.resize_60x60, name="resize_60x60"),


    path("meeting_list", views.MeetingList.as_view(), name="meeting_list"),
    path("meeting_detail/<int:pk>", views.MeetingDetail.as_view(), name="meeting_detail"),
    path("meeting_create", views.MeetingCreate.as_view(), name="meeting_create"),
    path("meeting_update/<int:pk>", views.MeetingUpdate.as_view(), name="meeting_update"),
    path("meeting_delete/<int:pk>", views.meeting_delete, name="meeting_delete"),

    path("set_coords", views.set_coords, name="set_coords"),
]