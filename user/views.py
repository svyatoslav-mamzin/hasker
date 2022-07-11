from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect

from forum.views import _get_trending
from user.forms import UserUpdateForm, UserProfileForm, SignUpForm
from user.models import Profile, AVATAR_DEFAULT


@login_required
@transaction.atomic
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('user_profile')
        else:
            pass
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)
    return render(request, 'profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': f'@{request.user.username} Profile',
        'trending': _get_trending(),
    })


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form,
                                                        'title': 'Sign Up',
                                                        'trending': _get_trending(),
                                                        })


@login_required
def set_default_avatar(request):
    user_profile = Profile.objects.get(user=request.user)
    user_profile.avatar = AVATAR_DEFAULT
    user_profile.save()
    return redirect('user_profile')

