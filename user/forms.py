from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from forum.utils import crop_square
from user.models import Profile


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = Profile
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = Profile
        # Add all the fields you want a user to change
        fields = ('first_name', 'last_name', 'email')


class UserProfileForm(forms.ModelForm):
    avatar = forms.ImageField(required=False, widget=forms.FileInput)

    class Meta:
        model = Profile
        fields = ('about', 'avatar')

    def clean_avatar(self):
        avatar = self.cleaned_data['avatar']

        try:
            # validate content type
            main, sub = avatar.content_type.split('/')
            if not (main == 'image' and sub in ['jpeg', 'pjpeg', 'png']):  # гифки идут нахер!
                raise ValidationError(_('Please use a JPEG or PNG image.'))

            # validate file size
            if len(avatar) > (1024 * 1024):
                raise ValidationError(_('Avatar file size may not exceed 1M.'))
            avatar.file = crop_square(avatar, sub)

        except AttributeError:
            """
            Handles case when we are updating the user profile
            and do not supply a new avatar
            """
            pass

        return avatar