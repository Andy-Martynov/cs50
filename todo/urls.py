from django.urls import path
from . import views

app_name = 'todo'
urlpatterns = [
    path("", views.index, name="index"),

    path("create", views.TaskCreate.as_view(), name="task_create"),
    path("create/<int:parent_id>", views.TaskCreate.as_view(), name="task_create"),
    path("create/<int:link_id>/<str:mode>", views.TaskCreate.as_view(), name="task_create"),

    path("check", views.check, name="check"),

    path("share/<int:pk>", views.task_share, name="task_share"),
    path("add_share", views.add_share, name="add_share"),
    path("remove_share", views.remove_share, name="remove_share"),

    path("update/<int:pk>", views.TaskUpdate.as_view(), name="task_update"),
    path("delete/<int:pk>", views.task_delete, name="task_delete"),
    path("recieve/<int:share_id>", views.recieve, name="recieve"),
    path("accept/<int:share_id>", views.accept, name="accept"),
    path("reject/<int:share_id>", views.reject, name="reject"),
    path("detail/<int:pk>", views.TaskDetail.as_view(), name="task_detail"),
    path("list", views.TaskList.as_view(), name="task_list"),

    path("preview/<int:share_id>", views.preview, name="preview"),
    path("reminder/<int:share_id>/<int:user_id>", views.reminder, name="reminder"),
]