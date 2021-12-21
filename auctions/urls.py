from django.urls import path

from . import views

app_name='auctions'
urlpatterns = [
    path("", views.index, name="index"),
    path("categories", views.categories, name="categories"),
    path("listing-create", views.ListingCreate.as_view(), name="listing-create"),
    path("listing-list/<int:category_id>", views.ListingList.as_view(), name="listing-list"),
    path("listing-detail/<int:pk>", views.ListingDetail.as_view(), name="listing-detail"),
    path("listing-edit/<int:pk>", views.ListingUpdate.as_view(), name="listing-update"),
    path("listing-delete/<int:pk>", views.ListingDelete.as_view(), name="listing-delete"),
    path("listing-close/<int:listing_id>", views.ListingClose, name="listing-close"),
    path("comment-create/<int:listing_id>", views.CommentCreate, name="comment-create"),
    path("bid-create/<int:listing_id>", views.BidCreate, name="bid-create"),
    path("watch-create/<int:listing_id>", views.WatchCreate, name="watch-create"),
    path("watch-delete/<int:watch_id>", views.WatchDelete, name="watch-delete"),
    path("watch-list/<int:user_id>", views.WatchList.as_view(), name="watch-list"),
    # path("login", views.login_view, name="login"),
    # path("logout", views.logout_view, name="logout"),
    # path("register", views.register, name="register")
]
