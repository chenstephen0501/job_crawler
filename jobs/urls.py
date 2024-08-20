from django.urls import path
from .views import fetch_cake_jobs, fetch_cake_jobs_all, user_apply_jobs, user_login

app_name = "jobs"

urlpatterns = [
    path("fetch_cake/", fetch_cake_jobs, name="fetch_cake_jobs"),
    path("fetch_cake_all/", fetch_cake_jobs_all, name="fetch_cake_jobs_all"),
    path("user_login/", user_login, name="user_login"),
    path("user_apply_jobs/", user_apply_jobs, name="user_apply_jobs")
]