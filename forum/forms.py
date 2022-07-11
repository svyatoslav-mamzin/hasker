from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from forum.models import Question, Answer


class NewQuestionForm(forms.ModelForm):
    tags = forms.CharField(required=True, max_length=255)

    class Meta:
        model = Question
        fields = ('title', 'content', 'tags',)

    def clean_tags(self):
        tags = self.cleaned_data['tags']
        if not tags:
            raise ValidationError(_('You need type at least one tag'))
        elif len(tags.split(',')) > 3:
            raise ValidationError(_('Max 3 tags allowed'))

        return tags


class NewAnswerForm(forms.ModelForm):

    class Meta:
        model = Answer
        fields = ('content',)
