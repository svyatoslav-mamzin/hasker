from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    path('user/', login_required(views.ProfileView.as_view()), name='user_prof'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('set_default_avatar/', views.set_default_avatar, name='set_default_avatar'),
]