from django.urls import path

from medications import views

app_name = "medications"

urlpatterns = [
    path("lookup/", views.medicine_lookup, name="lookup"),
    path("reminders/", views.reminder_list, name="reminder_list"),
    path("reminders/<int:reminder_id>/take/", views.mark_taken, name="mark_taken"),
]
