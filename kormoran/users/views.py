from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from .forms import RegisterForm, UserLoginForm
from .decorators import user_authenticated, user_not_authenticated
# Create your views here.

@user_not_authenticated
def register_user(request):
    if request.user.is_authenticated:
        return redirect("panel:home-view")

    if request.method == "POST":
        registration_form = RegisterForm(request.POST)

        if registration_form.is_valid():
            user = registration_form.save(commit=False)
            user.save()
            messages.success(
                request, "Your account have been created successfully. Please register now")
            return redirect("users:login-view")
        else:
            for error in list(registration_form.errors.values()):
                messages.error(request, error)
    else:
        registration_form = RegisterForm()
    return render(request, "users/register.html", {"registration_form": registration_form, })

@user_not_authenticated
def login_user(request):
    if request.method == "POST":
        auth_form = UserLoginForm(request=request, data=request.POST)
        if auth_form.is_valid():
            user = authenticate(
                username=auth_form.cleaned_data['username'],
                password=auth_form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                messages.success(
                    request, "You have been signed in successfully!")
                return redirect("panel:home-view")
        else:
            for error in list(auth_form.errors.values()):
                print(error)
                messages.error(request, error)

    else:
        auth_form = UserLoginForm()
    return render(request, "users/login.html", {"auth_form": auth_form})

@user_authenticated
def logout_user(request):
    logout(request)
    messages.success(request, "You were Logged Out successfully")
    return redirect("panel:home-view")
