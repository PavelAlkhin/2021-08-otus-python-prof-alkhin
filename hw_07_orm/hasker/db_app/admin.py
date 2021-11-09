from django.contrib import admin

# Register your models here.
from db_app.models import UserProfile, Question, Answer, Tag


@admin.register(UserProfile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'user', 'nick_name', 'avatar', 'register_date', 'email')
    list_display_links = ('id', '__str__')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__')
    list_display_links = ('id', '__str__')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'question')
    list_display_links = ('id', '__str__')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__')
    list_display_links = ('id', '__str__')