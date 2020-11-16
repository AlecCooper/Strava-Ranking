from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.models import Group

def login_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("/ranking/login")
        return view_func(request, *args, **kwargs)
    return wrapper_func

def is_authenticated(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/ranking")
        return view_func(request, *args, **kwargs)
    return wrapper_func

def allowed_user(view_func):
    def wrapper_func(request, ranking_name, *args, **kwargs):

        if request.user.groups.exists():
            group = Group.objects.get(name=ranking_name)
            user_groups = request.user.groups.all()
            if group in user_groups:
                return view_func(request, ranking_name, *args, **kwargs)

        return HttpResponse("Not Authorized to View Content")
    return wrapper_func

