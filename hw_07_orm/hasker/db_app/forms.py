from django.contrib.auth.models import User
from django import forms
from django.forms import Textarea

from db_app.models import UserProfile, Question, Answer, Tag


class UserForm(forms.ModelForm):
    password = forms.PasswordInput()

    class Meta:
        model = User
        fields = ('password',)


class UploadFileForm(forms.Form):
    # title = forms.CharField(max_length=50)
    avatar = forms.FileField()


class ProfileForm(forms.ModelForm):
    nick_name = forms.CharField(
        max_length=30
    )
    password = forms.CharField(max_length=30, required=False)
    # avatar = forms.FileField(label='Avatar', required=False, widget=forms.FileInput())
    avatar = forms.FileField(label='Avatar', required=False, widget=forms.ClearableFileInput(attrs={'multiple': False}))
    email = forms.EmailField(required=False, label='Your Email Address')
    register_date = forms.DateField(required=False, label='Date', widget=forms.DateInput(
        format=('%Y-%m-%d'), attrs={'class': 'form-control', 'placeholder': 'Select a date',
                                    'type': 'date'}
    ))

    class Meta:
        model = UserProfile
        fields = ('nick_name', 'avatar', 'register_date', 'email')
        # widgets = {
        #     'register_date': forms.DateInput(
        #         format=('%Y-%m-%d'),
        #         attrs={'class': 'form-control',
        #                'placeholder': 'Select a date',
        #                'type': 'date'
        #                }),
        # }


# class UserForm(forms.Form):
#     nick_name = forms.CharField(
#         max_length=3
#     )
#     date_joined = forms.DateInput()
#     password = forms.CharField()
#     email = forms.EmailInput()
#
#
# class ProfileForm(forms.Form):
#     nick_name = forms.CharField(
#         max_length=3
#     )
#     avatar = forms.FileField()


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('title', 'description')
        widgets = {
            'description': Textarea(attrs={'cols': 80, 'rows': 20}),
        }

    tags_form = forms.CharField()

    # tags = forms.ModelMultipleChoiceField(
    #     queryset=Tag.objects.all(),
    #     widget=forms.CheckboxSelectMultiple
    # )


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('author', 'description', 'is_right')
