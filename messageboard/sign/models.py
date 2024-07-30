from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.db import models

from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group


class OneTimeCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.email} - {self.code}'


class OneTimeCodeForm(forms.Form):
    code = forms.CharField(label="Введите одноразовый код", max_length=6)


class BaseRegisterForm(UserCreationForm):
    email = forms.EmailField(label="Email")

    class Meta:
        model = User
        fields = ("email",
                  "password1",
                  "password2",)
