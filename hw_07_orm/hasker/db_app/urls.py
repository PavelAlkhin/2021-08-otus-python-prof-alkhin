"""hasker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.urls import path
from . import views

app_name = "db_app"

urlpatterns = [
    path('', views.IndexPageView.as_view(), name='index'),
    path('profile/', views.update_profile, name='profile'),
    path('question/<int:id>', views.QuestionDetailView.as_view(), name='Question datail'),
    path('ask/', views.QuestionProceed.as_view(), name='ask_question'),
    # url(
    #         regex=r'^(?P<pk>\d+)/$',
    #         view=views.QuestionDetailView.as_view(),
    #         name='detail'
    #     ),
    path('answer/', views.update_profile, name='answer'),

]
