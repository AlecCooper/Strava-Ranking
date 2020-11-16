from django.shortcuts import render, HttpResponse, get_object_or_404, redirect, HttpResponseRedirect
from django.template import loader
from django.contrib.auth.models import Group, Permission, User
from django.contrib.auth import logout
from django.contrib.sites.shortcuts import get_current_site
from allauth.socialaccount.models import SocialToken, SocialAccount
import requests
from .models import Ranking, Segment, Performance, Profile
from .forms import createRankingForm, rankingForm
from .decorators import login_required, allowed_user, is_authenticated

#@login_required
def logout_page(request):

    logout(request)

    return HttpResponse("logged out")

@login_required
def index(request):

    template = loader.get_template('ranking_app/index.html')

    # Get the rankings the user is a member of
    groups = request.user.groups.all()

    rankings = []
    for group in groups:
        rankings.append(Ranking.objects.get(name=group.name))

    # Get user details
    user = request.user
    social_account = SocialAccount.objects.get(user=user)
    extra_data = social_account.extra_data
    first_name = extra_data["firstname"]

    context = {'rankings':rankings}

    return HttpResponse(template.render(context, request))

@is_authenticated
def login(request):

    template = loader.get_template('ranking_app/login.html')

    host = request.get_host()

    context = {"host":host}

    return HttpResponse(template.render(context, request))

@login_required
@allowed_user
def ranking(request, ranking_name):

    ranking = get_object_or_404(Ranking, name=ranking_name)

    # Get the segments associated with the ranking
    segments = Segment.objects.filter(ranking__name=ranking_name)

    form = rankingForm

    # Get our template
    template = loader.get_template('ranking_app/ranking.html')

    # Reload segments incase we have added one
    segments = Segment.objects.filter(ranking__name=ranking_name)

    # Get the rankings
    ranked = ranking.get_ranking()

    context = {
        'ranking':ranking,
        'segments':segments,
        'ranked':ranked
    }

    return HttpResponse(template.render(context, request))

@login_required
@allowed_user
def edit_ranking(request, ranking_name):

    # Get the ranking
    ranking = get_object_or_404(Ranking, name=ranking_name)

    # Get the segments associated with the ranking
    segments = Segment.objects.filter(ranking__name=ranking_name)

    form = rankingForm

    if request.method == "POST":
        form = rankingForm(request.POST)

        if form.is_valid():

            # Add Segment Form
            if not form.cleaned_data['segment_url'] == "":

                url = form.cleaned_data['segment_url']
                segment = Segment.create(url, ranking, request)

                # Confirm segment is unique
                if not Segment.objects.filter(ranking__name=ranking.name, segment_id=segment.segment_id).exists():
                    segment.save()

                    # We need to create a preformance for each user
                    users = User.objects.filter(groups__name=ranking.name)
                    
                    # Create a preformance for each user
                    for p_user in users:
                        performance = Performance.create(p_user, segment)
                        performance.save()

            # Add User Form
            elif not form.cleaned_data['add_user'] == "":

                username = form.cleaned_data['add_user']

                # Add the user
                group = Group.objects.get(name=ranking.name)
                group.user_set.add(User.objects.get(username=username))
                group.save()

    context = {
        'form':form,
        'ranking':ranking,
    }

    # Get our template
    template = loader.get_template('ranking_app/edit.html')

    return HttpResponse(template.render(context, request))

@login_required
def create_ranking(request):

    form = createRankingForm()

    if request.method == "POST":
        form = createRankingForm(request.POST)

        if form.is_valid():
            Ranking.objects.create(**form.cleaned_data)

            # Create the group associated with the ranking, add user and save
            group = Group.objects.create(name=form.cleaned_data['name'])
            perm = Permission.objects.get(name='Is a member of the ranking')
            group.permissions.add(perm)
            group.save()
            user = request.user
            group.user_set.add(user)
            user.save()
            group.save()
            
            return HttpResponseRedirect('/ranking/' + form.cleaned_data['name'])

        else:
            print(form.errors)
        
    context = {'form':form}

    return render(request, 'ranking_app/create.html', context)

@login_required
@allowed_user
def segment(request, ranking_name, segment_name):

    ranking = get_object_or_404(Ranking, name=ranking_name)
    segment = get_object_or_404(Segment, name=segment_name, ranking__name=ranking_name)

    # get sorted list of performances
    performances = segment.get_ranking()

    template = loader.get_template('ranking_app/segment.html')

    context = {
        "ranking":ranking,
        "segment":segment,
        "ranked":performances
    }

    return HttpResponse(template.render(context, request))

@login_required
@allowed_user
def profile(request, ranking_name, profile_name):

    # Get the ranking and user objects
    ranking = get_object_or_404(Ranking, name=ranking_name)
    user = get_object_or_404(User, username=profile_name)
    profile = get_object_or_404(Profile, user=user)
    social_account = get_object_or_404(SocialAccount, user=user)

    extra_data = social_account.extra_data
    first_name = extra_data["firstname"]
    last_name = extra_data["lastname"]

    profile_url = social_account.get_profile_url()

    ranked = profile.get_segments(ranking)

    template = loader.get_template('ranking_app/user.html')

    context = {
        "ranking":ranking,
        "user":user,
        "ranked":ranked,
        "firstname":first_name,
        "lastname":last_name,
        "profile_url":profile_url
    }

    return HttpResponse(template.render(context, request))


