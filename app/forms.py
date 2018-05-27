from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from app.models import User, Exam


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "timezone")
