import os
import requests
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, reverse
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth.forms import UserCreationForm
from django.core.files.base import ContentFile
from . import models as users_models
from . import forms


# Create your views here.
class LoginView(FormView):
    template_name = "users/login.html"
    form_class = forms.LoginForm
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        auth_user = form.cleaned_data["auth_user"]
        if auth_user:
            login(self.request, user=auth_user)
        return super().form_valid(form)


def log_out(request):
    logout(request)
    return redirect(reverse("core:home"))


class SignUpView(FormView):

    template_name = "users/signup.html"
    form_class = forms.SignUpForm
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        form.save(commit=True)
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user:
            login(self.request, user)
        user.verify_email()
        return super().form_valid(form)


def complete_verification(request, key):
    try:
        user = users_models.User.objects.get(email_secret=key)
        user.email_verify = True
        user.email_secret = ""
        user.save()
        # todo : success message
    except users_models.User.DoesNotExist:
        # todo : add error messsage
        pass
    return redirect(reverse("core:home"))


def github_login(request):
    client_id = os.environ.get("GH_ID")
    redirect_uri = "http://127.0.0.1:8000/users/login/github/callback"
    scope = "read:user"
    return redirect(
        f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}",
    )


class GithubException(Exception):
    pass


def github_callback(request):
    try:
        client_id = os.environ.get("GH_ID")
        client_secret = os.environ.get("GH_SECRET")
        code = request.GET.get("code", None)
        if code is not None:
            token = requests.post(
                f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}",
                headers={"Accept": "application/json"},
            )
            token_json = token.json()
            error = token_json.get("error", None)
            if error is not None:
                raise GithubException()
            else:
                access_token = token_json.get("access_token")
                profile_request = requests.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"token {access_token}",
                        "Accept": "application/json",
                    },
                )
            profile_json = profile_request.json()
            username = profile_json.get("login", None)
            if username is not None:
                name = profile_json.get("name", None)
                email = profile_json.get("email", None)
                bio = profile_json.get("bio", None)
                try:
                    user = users_models.User.objects.get(email=email)
                    if user.login_method != users_models.User.LOGIN_GITHUB:
                        raise GithubException()
                except users_models.User.DoesNotExist:
                    user = users_models.User.objects.create(
                        email=email,
                        first_name=name,
                        username=email,
                        bio=bio,
                        login_method=users_models.User.LOGIN_GITHUB,
                        email_verify=True,
                    )
                    user.set_unusable_password()
                    user.save()
                login(request, user)
                return redirect(reverse("core:home"))

            else:
                raise GithubException()

        else:
            raise GithubException()
    except GithubException:
        return redirect(reverse("users:login"))


class KakaoException(Exception):
    pass


def kakao_login(req):
    REST_API_KEY = os.environ.get("KAKAO_REST_API_KEY")
    REDIRECT_URI = "http://127.0.0.1:8000/users/login/kakao/callback"

    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}&response_type=code"
    )


def kakao_callback(req):

    code = req.GET.get("code")
    grant_type = "authorization_code"
    client_id = os.environ.get("KAKAO_REST_API_KEY")
    redirect_uri = "http://127.0.0.1:8000/users/login/kakao/callback"
    token = requests.post(
        f"https://kauth.kakao.com/oauth/token?code={code}&grant_type={grant_type}&client_id={client_id}&redirect_uri={redirect_uri}",
        headers={"application": "x-www-form-urlencoded;charset=utf-8"},
    )

    token_json = token.json()
    error = token_json.get("error", None)

    if error is not None:
        raise KakaoException()
    access_token = token_json.get("access_token")
    profile_request = requests.post(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    profile_json = profile_request.json()
    kakao_account = profile_json.get("kakao_account")
    email = kakao_account["email"]
    if email is None:
        raise KakaoException()
    profile = kakao_account["profile"]
    nickname = profile["nickname"]
    profile_image_url = profile["profile_image_url"]
    try:
        user = users_models.User.objects.get(email=email)
        if user.login_method != users_models.User.LOGIN_KAKAO:
            raise KakaoException()
    except users_models.User.DoesNotExist:
        user = users_models.User.objects.create(
            email=email,
            username=email,
            first_name=nickname,
            login_method=users_models.User.LOGIN_KAKAO,
            email_verify=True,
        )
        user.set_unusable_password()
        user.save()
        if profile_image_url is not None:
            photo_request = requests.get(profile_image_url)
            user.avatar.save(
                f"{nickname}_avatar",
                ContentFile(photo_request.content),
                save=True,
            )
            user.save()
    login(req, user)
    return redirect(reverse("core:home"))
