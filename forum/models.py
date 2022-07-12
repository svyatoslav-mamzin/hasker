from django.db import models
from user.models import Profile


class Tag(models.Model):
    tagword = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.tagword}"


class Question(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    tags = models.ManyToManyField(Tag, verbose_name="list of tags",
                                  blank=True, default=None)
    likes = models.ManyToManyField(Profile, verbose_name="q_liked from",
                                   default=None, related_name="q_liked_from")
    dislikes = models.ManyToManyField(Profile, verbose_name="q_disliked from",
                                      default=None, related_name="q_disliked_from")
    rating = models.IntegerField(default=0)
    votes = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return f"{self.title[:50]}"


class Answer(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    content = models.TextField()
    is_solution = models.BooleanField(default=False)
    likes = models.ManyToManyField(Profile, verbose_name="a_liked from",
                                   default=None, related_name="a_liked_from")
    dislikes = models.ManyToManyField(Profile, verbose_name="a_disliked from",
                                      default=None, related_name="a_disliked_from")
    rating = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return f"{self.content[:50]}"

