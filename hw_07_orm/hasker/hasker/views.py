from django.shortcuts import render, redirect


def home(request):
    return redirect("db_app:index")


def profile(request):
    return redirect("db_app:profile")