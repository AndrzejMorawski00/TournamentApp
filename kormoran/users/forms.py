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

        self.fields["first_name"].widget.attrs.update({
            'class': 'form__input',
            'placeholder' : 'First Name',
            'id' : 'first_name',
        })
        self.fields["last_name"].widget.attrs.update({
            'class': 'form__input',
            'placeholder' : 'Last Name',
            'id' : 'last_name',
        })
        self.fields["username"].widget.attrs.update({
            'class': 'form__input',
            'placeholder' : 'Username',
            'id' : 'username',
        })
        self.fields["email"].widget.attrs.update({
            'class': 'form__input',
            'placeholder' : 'Email',
            'id' : 'email',
        })
        self.fields["password1"].widget.attrs.update({
            'class': 'form__input',
            'placeholder' : 'Password',
            'id' : 'password1',
        })
        self.fields["password2"].widget.attrs.update({
            'class': 'form__input',
            'placeholder' : 'Repeat Password',
            'id' : 'password2',
        })


class UserLoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form__input', 'id': 'form__username', 'placeholder': 'Username or Email'}),
        label="Username or Email")

    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form__input', 'id': 'form__password', 'placeholder': 'Password'}),
        label="Password")
