from django.urls import path

from . import views

urlpatterns = [
    path('user/', views.profile, name='user_prof'),
    path('signup/', views.signup, name='signup'),
    path('set_default_avatar/', views.set_default_avatar, name='set_default_avatar'),
]