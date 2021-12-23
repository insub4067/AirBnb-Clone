from django import forms
from . import models
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import (
    MinimumLengthValidator,
    CommonPasswordValidator,
    NumericPasswordValidator,
)


class LoginForm(forms.Form):

    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": "이메일"}))
    password = forms.CharField( widget=forms.PasswordInput(attrs={"placeholder": "비밀번호"}))

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        user = models.User.objects.filter(username=email).exists()

        if user:
            auth_user = authenticate(username=email, password=password)
            if not auth_user:
                self.add_error("password", "유저정보가 일치하지 않습니다")
            return {"email": email, "password": password, "auth_user": auth_user}
        else:
            self.add_error("password", "유저정보가 존재하지 않습니다")


class SignUpForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ["email", "password"]
        widgets = {
            "email": forms.EmailInput(attrs={"placeholder": "이메일"}),
        }

    min_length = 12

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "비밀번호"}),
        validators=[
            MinimumLengthValidator(min_length).validate,
            CommonPasswordValidator().validate,
            NumericPasswordValidator().validate,
        ],
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "중복확인"}),
        validators=[
            MinimumLengthValidator(min_length).validate,
            CommonPasswordValidator().validate,
            NumericPasswordValidator().validate,
        ],
    )

    def clean_password1(self):
        password = self.cleaned_data.get("password")
        password1 = self.cleaned_data.get("password1")

        if password != password1:
            self.add_error("password", "비밀번호가 일치하지 않습니다")
            self.add_error("password1", "비밀번호가 일치하지 않습니다")
        return password

    def clean_email(self):
        email = self.cleaned_data.get("email")
        user = models.User.objects.filter(username=email)
        if user.exists():
            self.add_error("email", "이미 가입된 이메일 입니다")
        else:
            return email

    def save(self, *args, **kwargs):
        user = super().save(commit=False)
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password1")
        user.username = email
        user.set_password(password)
        user.save()
