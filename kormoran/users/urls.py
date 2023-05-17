from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("login-user/", views.login_user, name="login-view"),
    path("register-user/", views.register_user, name="register-view"),
    path("logout-user/", views.logout_user, name="logout-view")
]
