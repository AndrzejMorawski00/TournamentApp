from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    username = forms.CharField(max_length=100, required=True)
    email = forms.CharField(
        max_length=100, required=True, widget=forms.EmailInput)
    password1 = forms.CharField(max_length=100, widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=100, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username",
                  "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields["first_name"].label = "First Name:"
        self.fields["last_name"].label = "Last Name:"
        self.fields["username"].label = "Username:"
        self.fields["email"].label = "Email:"
        self.fields["password1"].label = "Password:"
        self.fields["password2"].label = "Repeat Password:"


class UserLoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username or Email'}),
        label="Username or Email")

    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}),
        label="Password")
