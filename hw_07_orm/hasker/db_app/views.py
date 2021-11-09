import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils.dateparse import parse_date

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView, FormView

from db_app.forms import ProfileForm, QuestionForm, UploadFileForm
from db_app.models import UserProfile, Question, Answer


def render_context(request, resource, context=None):
    return render(
        request,
        resource,
        context=context,
    )


class IndexPageView(TemplateView):
    template_name = 'db_app/index.html'

    def get(self, request, **kwargs):
        questions = Question.objects.all()
        ctx = {
            'questions': []
        }
        for q in questions:
            c_answers = Answer.objects.filter(question=q).all().count()
            ctx['questions'].append({
                'question': q,
                'count_answers': c_answers
            })

        return render_context(request=request,
                              resource=self.template_name,
                              context=ctx)

    @method_decorator(csrf_protect, name='dispatch')
    def post(self, request, **kwargs):
        pass


class QuestionProceed(TemplateView):
    template_name = 'db_app/ask_question.html'

    # form_class = QuestionForm

    def get(self, request, **kwargs):
        # q_title = request.GET.get('title', '')
        # if q_title != '':
        #     quest = Question.objects.get(title=q_title)
        #     question_form = QuestionForm(instance=quest)
        # else:
        #     question_form = QuestionForm()
        question_form = QuestionForm()
        ctx = {
            'question_form': question_form,
        }
        return render_context(request=request, resource=self.template_name,
                              context=ctx)

    @method_decorator(csrf_protect, name='dispatch')
    def post(self, request, **kwargs):
        question_form = QuestionForm(request.POST, instance=Question())
        question = question_form.save(commit=False)
        question.author = request.user
        question.date = datetime.datetime.now()
        question.save()
        return redirect('/')


def handle_uploaded_file(f, user):
    with open(user_directory_path(user, f.name), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def user_directory_path(user, filename):
    """file will be uploaded to MEDIA_ROOT / user_<id>/<filename>"""
    return 'db_app/static/db_app/img/user_{0}/{1}'.format(user.id, filename)


@login_required
@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        avatar_clear = request.POST.get('avatar-clear', False)
        if avatar_clear:
            avatar = ''
        else:
            try:
                avatar = request.FILES['avatar'].name
            except:
                avatar = request.user.userprofile.avatar
        file_form = UploadFileForm(request.POST, request.FILES)
        if file_form.is_valid():
            handle_uploaded_file(request.FILES['avatar'], request.user)

        # profile_form = ProfileForm(request.POST, instance=request.user.profile)
        # if profile_form.is_valid():
        #     profile_form.save(commit=False)
        #     profile_form.user = request.user
        #     profile_form.save()
        #
        # return render(request, 'db_app/profile.html', {
        #     # 'user_form': user_form,
        #     'profile_form': profile_form
        # })

        nick_name = request.POST.get('nick_name', '')
        register_date = parse_date(request.POST.get('register_date', ''))
        email = request.POST.get('email', '')
        try:
            profile = request.user.userprofile
        except:
            try:
                profile = UserProfile.objects.get(user=request.user)
            except:
                profile = UserProfile()
                profile.user = request.user

            # profile_form = ProfileForm(request.POST)
            # if user_form.is_valid() and profile_form.is_valid():
            #     profile_form.user = request.user
            #     # user_form.fields['profile'] = profile_form
            #     # user_form.save()
            #     # print(profile_form.register_date)
            #     profile = profile_form.save(commit=False)
            #     profile.save()
            #
            #     # profile = Profile(user=request.user, nick_name=profile_form.nick_name,
            #     #                   register_date=profile_form.register_date,
            #     #                   email=profile_form.email)
            #     # profile.save()
            # else:
            #     messages.error(request, 'Пожалуйста, исправьте ошибки.')

        profile.nick_name = nick_name
        profile.avatar = avatar
        profile.register_date = register_date
        profile.email = email
        profile.save()

        profile_form = ProfileForm(instance=profile)
        messages.success(request, 'Ваш профиль был успешно обновлен!')
        return redirect('db_app:profile')
    else:
        # user_form = UserForm(instance=request.user)
        try:
            profile_form = ProfileForm(instance=request.user.profile)
        except:
            # try:

            # user_profile = UserProfile.objects.get(user=request.user)
            # profile_form = ProfileForm(user_profile)
            # except:
            #     profile_form = ProfileForm()
            try:
                user_profile = UserProfile.objects.get(user=request.user)
                profile_form = ProfileForm(instance=user_profile)
            except UserProfile.DoesNotExist:
                profile_form = ProfileForm()
    return render(request, 'db_app/profile.html', {
        # 'user_form': user_form,
        'profile_form': profile_form
    })


class QuestionDetailView(TemplateView):
    template_name = 'db_app/question_detail.html'

    # form_class = QuestionForm

    def get(self, request, **kwargs):
        # title = request.GET.get('title', '')
        id_ = kwargs.get('id', '')
        quest = Question.objects.get(pk=id_)
        question_form = QuestionForm(instance=quest)
        try:
            answers = Answer.objects.filter(question=quest).all()
        except:
            answers = list()

        ctx = {
            'question_form': question_form,
            'title': quest.title,
            'description': quest.description,
            'tags': quest.tags.all(),
            'question_id': quest.id,
            'answers': answers,
            'author': quest.author
        }
        return render_context(request=request,
                              resource=self.template_name,
                              context=ctx)

    @method_decorator(csrf_protect, name='dispatch')
    def post(self, request, **kwargs):
        user = request.user
        question_id = request.POST.get('question_id', '')
        current_answer = request.POST.get('current_answer', '')
        quest = Question.objects.get(pk=question_id)
        Answer(description=current_answer,
               question=quest,
               author=user,
               date=datetime.datetime.now()).save()
        return redirect(f'/question/{question_id}')
