from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views import View

from forum.views import _get_trending
from user.forms import UserUpdateForm, UserProfileForm, SignUpForm
from user.models import Profile


class ProfileView(View):
    user_form = UserUpdateForm
    profile_form = UserProfileForm

    @method_decorator(transaction.atomic)
    def post(self, request):
        user_form = self.user_form(request.POST, instance=request.user)
        profile_form = self.profile_form(request.POST, request.FILES, instance=request.user)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('user_prof')

    def get(self, request):
        user_form = self.user_form(instance=request.user)
        profile_form = self.profile_form(instance=request.user)
        return render(request, 'profile.html', {
            'user_form': user_form,
            'profile_form': profile_form,
            'title': f'@{request.user.username} Profile',
            'trending': _get_trending(),
        })


class SignupView(View):
    form = SignUpForm

    def get(self, request):
        return render(request, 'registration/signup.html', {'form': self.form(),
                                                            'title': 'Sign Up',
                                                            'trending': _get_trending(),
                                                            })

    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')


@login_required
def set_default_avatar(request):
    user_profile = Profile.objects.get(user=request.user)
    user_profile.avatar = settings.AVATAR_DEFAULT
    user_profile.save()
    return redirect('user_prof')

