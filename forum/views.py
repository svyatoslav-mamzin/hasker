import json
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.contrib.postgres.search import SearchVector
from forum.forms import SignUpForm, UserUpdateForm, UserProfileForm, NewQuestionForm, NewAnswerForm
from forum.models import Profile, Tag, Question, Answer, AVATAR_DEFAULT
from forum.utils import send_answer_mail


def index(request):
    questions = Question.objects.all().select_related('author').prefetch_related('tags', 'answers').order_by('-votes')
    paginator = Paginator(questions, 20)
    page = request.GET.get('page')
    questions = paginator.get_page(page)
    return render(request, 'forum/index.html', {'questions': questions,
                                                    'title': 'Home',
                                                    'trending': _get_trending(),})


def new(request):
    questions = Question.objects.all().select_related('author').prefetch_related('tags', 'answers').order_by('-created')
    paginator = Paginator(questions, 20)
    page = request.GET.get('page')
    questions = paginator.get_page(page)
    return render(request, 'forum/new.html', {'questions': questions,
                                                    'title': 'New Questions',
                                                    'trending': _get_trending(),})


def search(request):
    search_query = request.GET.get('q')
    if search_query.startswith('tag:'):
        return tag_search(request, search_query[4:])
    searchv = SearchVector('title', 'content')
    searchv.default_alias = 'question_search'
    found = Question.objects.annotate(search=searchv).filter(search=search_query)\
        .order_by('-rating', '-created')
    paginator = Paginator(found, 20)
    page = request.GET.get('page')
    questions = paginator.get_page(page)
    return render(request, 'forum/search.html', {'questions': questions,
                                                     'title': f'Search: "{search_query}"',
                                                     'search_query': search_query,
                                                     'count': paginator.count,
                                                     'trending': _get_trending(), })


def tag_search(request, tagword):
    searchv = SearchVector('tags')
    searchv.default_alias = 'tag_search'
    found = Question.objects.filter(tags__tagword__iexact=tagword).order_by('-rating', '-created')
    paginator = Paginator(found, 20)
    page = request.GET.get('page')
    questions = paginator.get_page(page)
    return render(request, 'forum/tag.html', {'questions': questions,
                                                  'title': f'Tag: #{tagword}',
                                                  'tagword': tagword,
                                                  'count': paginator.count,
                                                  'trending': _get_trending(), })


@transaction.atomic
def question(request, uid):
    if request.method == 'POST':
        form = NewAnswerForm(request.POST)
        if form.is_valid():
            pub = form.save(commit=False)
            pub.author = User.objects.get(username=request.user)
            pub.question = Question.objects.get(pk=uid)
            pub.save()
            send_answer_mail(to=pub.question.author.email, username=pub.question.author.username,
                             post_id=uid, question_title=pub.question.title)
            return redirect('question', uid)
    else:
        queryset = Question.objects.select_related('author', 'author__profile').prefetch_related('likes', 'dislikes')

        question = get_object_or_404(queryset, pk=uid)

        title = question.title
        is_owner = question.author.id == request.user.id
        # '-rating' change to 'created'
        answers = Answer.objects.filter(question__id=uid).select_related('author',  'author__profile')\
            .prefetch_related('likes', 'dislikes').order_by('-is_solution', 'created')
        form = NewAnswerForm()
        return render(request, 'forum/q.html', {'title': title,
                                                    'question': question,
                                                    'answers': answers,
                                                    'is_owner': is_owner,
                                                    'form': form,
                                                    'trending': _get_trending(),})


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
    return render(request, 'forum/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': f'@{request.user.username} Profile',
        'trending': _get_trending(),
    })


@login_required
@transaction.atomic
def ask(request):
    if request.method == 'POST':
        form = NewQuestionForm(request.POST)
        if form.is_valid():
            pub = form.save(commit=False)
            pub.author = User.objects.get(username=request.user)
            pub.save()
            pub.tags.clear()

            tags = str(request.POST.get('tags'))
            tags = [tag.strip() for tag in tags.split(',')]
            for tag in tags:
                obj, create = Tag.objects.get_or_create(tagword=tag)
                pub.tags.add(obj)
            pub.save()
            return redirect('question', pub.id)
        else:
            print(form.errors)
    else:
        form = NewQuestionForm(instance=request.user)
    return render(request, 'forum/ask.html', {
        'form': form,
        'title': 'Ask',
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


@login_required
def like_question(request, uid):
    user = request.user
    post = Question.objects.get(id=uid)
    post.dislikes.remove(user)
    post.likes.add(user)
    post.rating = post.likes.count() - post.dislikes.count()
    post.votes = post.likes.count() + post.dislikes.count()
    post.save()
    return HttpResponse(str(post.rating))


@login_required
def dislike_question(request, uid):
    user = request.user
    post = Question.objects.get(id=uid)
    post.likes.remove(user)
    post.dislikes.add(user)
    post.rating = post.likes.count() - post.dislikes.count()
    post.votes = post.likes.count() + post.dislikes.count()
    post.save()
    return HttpResponse(str(post.rating))


@login_required
def like_answer(request, ans_uid):
    user = request.user
    post = Answer.objects.get(id=ans_uid)
    post.dislikes.remove(user)
    post.likes.add(user)
    post.rating = post.likes.count() - post.dislikes.count()
    post.save()
    return HttpResponse(str(post.rating))


@login_required
def dislike_answer(request, ans_uid):
    user = request.user
    post = Answer.objects.get(id=ans_uid)
    post.likes.remove(user)
    post.dislikes.add(user)
    post.rating = post.likes.count() - post.dislikes.count()
    post.save()
    return HttpResponse(str(post.rating))


def send_all_tags(request):
    tags = Tag.objects.all()
    data = [tag.tagword for tag in tags]
    data = json.dumps(data)
    return HttpResponse(data, content_type='application/json')


def _get_trending():
    last_month = datetime.today() - timedelta(days=30)
    trending = Question.objects.filter(created__gte=last_month).prefetch_related('answers').order_by('-votes')[:15]
    return trending


@login_required
def set_answer_as_solution(request, ans_uid):
    user = request.user
    post = Answer.objects.get(id=ans_uid)
    if post.is_solution:
        return HttpResponse(f"Ne balyisya knopkoj!")
    if post.question.author.id == user.id:
        post.is_solution = True
        post.save()
        return HttpResponse(f"OK. Set answer id {ans_uid} as solution")
    else:
        return HttpResponse(f"Error. You are not author of this question! Where are you find this button?")
