from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('new/', views.NewView.as_view(), name='new_questions'),
    path('q/<int:uid>/', views.QuestionView.as_view(), name='question'),
    path('tag/<str:tagword>/', views.tag_search, name='tag_search'),
    path('ask/', login_required(views.AskView.as_view()), name='ask'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('q/<int:uid>/like/', views.LikeView.as_view(), name='like_question'),
    path('q/<int:uid>/dislike/', views.DislikeView.as_view(), name='dislike_question'),
    path('q/answer/<int:uid>/like/', views.LikeAnswerView.as_view(), name='like_answer'),
    path('q/answer/<int:uid>/dislike/', views.DislikeAnswerView.as_view(), name='dislike_answer'),
    path('q/answer/<int:uid>/is_solution/', views.set_answer_as_solution, name='set_answer_as_solution'),
    path('ajax/tags/push/', views.send_all_tags, name="send_all_tags"),
]
