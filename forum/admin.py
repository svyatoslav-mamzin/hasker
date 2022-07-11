from django.contrib import admin
from forum.models import Question, Answer, Tag


class QuestionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Question._meta.fields]

    class Meta:
        model = Question


admin.site.register(Question, QuestionAdmin)


class AnswerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Answer._meta.fields]

    class Meta:
        model = Answer


admin.site.register(Answer, AnswerAdmin)


class TagAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Tag._meta.fields]

    class Meta:
        model = Tag


admin.site.register(Tag, TagAdmin)
