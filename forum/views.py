import json
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.contrib.postgres.search import SearchVector
from django.utils.decorators import method_decorator
from django.views import View
from forum.forms import NewQuestionForm, NewAnswerForm
from forum.models import Tag, Question, Answer
from forum.utils import send_answer_mail
from user.models import Profile


class IndexView(View):
    paginate_by = 20
    template_name = 'forum/index.html'
    order_by = ('-votes',)
    title = 'Home'

    def get(self, request, *args, **kwargs):
        questions = Question.objects.all().select_related('author').prefetch_related('tags', 'answers')\
                                                                                .order_by(*self.order_by)
        paginator = Paginator(questions, self.paginate_by)
        page = request.GET.get('page')
        questions = paginator.get_page(page)
        return render(request, self.template_name, {'questions': questions,
                                                    'title': self.title,
                                                    'trending': _get_trending(), })


class NewView(IndexView):
    template_name = 'forum/new.html'
    order_by = ('-created',)
    title = 'New Questions'


class SearchView(View):
    model = Question
    args_search = ('title', 'content',)
    order_by = ('-rating', '-created',)
    paginate_by = 20
    template_name = 'forum/search.html'

    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('q')
        if search_query.startswith('tag:'):
            return tag_search(request, search_query[4:])
        searchv = SearchVector(*self.args_search)
        searchv.default_alias = 'question_search'
        found = self.model.objects.annotate(search=searchv).filter(search=search_query).order_by(*self.order_by)
        paginator = Paginator(found, self.paginate_by)
        page = request.GET.get('page')
        questions = paginator.get_page(page)
        return render(request, self.template_name, {'questions': questions,
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


class QuestionView(View):
    form = NewAnswerForm
    prefetch_related = ('likes', 'dislikes',)
    order_by = ('-is_solution', 'created',)
    template_name = 'forum/q.html'

    def get(self, request, uid, *args, **kwargs):
        queryset = Question.objects.select_related('author').prefetch_related(*self.prefetch_related)
        question = get_object_or_404(queryset, pk=uid)
        title = question.title
        is_owner = question.author.id == request.user.id
        answers = Answer.objects.filter(question__id=uid).select_related('author')\
            .prefetch_related(*self.prefetch_related).order_by(*self.order_by)
        form = self.form()
        return render(request, self.template_name, {'title': title,
                                                'question': question,
                                                'answers': answers,
                                                'is_owner': is_owner,
                                                'form': form,
                                                'trending': _get_trending(), })

    @method_decorator(transaction.atomic)
    def post(self, request, uid, *args, **kwargs):
        form = self.form(request.POST)
        if form.is_valid():
            pub = form.save(commit=False)
            pub.author = Profile.objects.get(username=request.user)
            pub.question = Question.objects.get(pk=uid)
            pub.save()
            send_answer_mail(to=pub.question.author.email,
                             username=pub.question.author.username,
                             post_id=uid,
                             question_title=pub.question.title)
            return redirect('question', uid)


class AskView(View):
    form = NewQuestionForm
    template_name = 'forum/ask.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': self.form(instance=request.user),
                                                    'title': 'Ask',
                                                    'trending': _get_trending()})

    @method_decorator(transaction.atomic)
    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        if form.is_valid():
            pub = form.save(commit=False)
            pub.author = Profile.objects.get(username=request.user)
            pub.save()
            pub.tags.clear()

            tags = str(request.POST.get('tags'))
            tags = [tag.strip() for tag in tags.split(',')]
            for tag in tags:
                obj, create = Tag.objects.get_or_create(tagword=tag)
                pub.tags.add(obj)
            pub.save()
            return redirect('question', pub.id)


class RatingBaseView(View):
    model = Question
    hash_attr_for_remove = 'dislikes'
    hash_attr_for_add = 'likes'

    @method_decorator(login_required)
    def get(self, request, uid, *args, **kwargs):
        user = request.user
        post = self.model.objects.get(id=uid)
        post.__getattribute__(self.hash_attr_for_remove).remove(user)
        post.__getattribute__(self.hash_attr_for_add).add(user)
        post.rating = post.likes.count() - post.dislikes.count()
        if hasattr(post, 'votes'):
            post.votes = post.likes.count() + post.dislikes.count()
        post.save()
        return HttpResponse(str(post.rating))


class LikeView(RatingBaseView):
    pass


class DislikeView(RatingBaseView):
    hash_attr_for_remove = 'likes'
    hash_attr_for_add = 'dislikes'


class LikeAnswerView(RatingBaseView):
    model = Answer


class DislikeAnswerView(RatingBaseView):
    model = Answer
    hash_attr_for_remove = 'likes'
    hash_attr_for_add = 'dislikes'


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
