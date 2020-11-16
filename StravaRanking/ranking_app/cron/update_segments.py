from django.contrib.auth.models import User, Group
from ranking_app.models import Ranking, Segment, Performance
from allauth.socialaccount.models import SocialToken
from ranking_app.strava import refresh_token
import requests
import math

# Get all users 
users = User.objects.exclude(username="admin")

for user in users:

    # Get the social token for our user
    token = SocialToken.objects.get(account__user=user, account__provider='strava')

    # Refresh token
    token = refresh_token(user)

    # All performances associated with the user
    performances = Performance.objects.filter(owner=user)

    # Make an api call to update each performance for the user
    for performance in performances:

        segment = performance.segment
        segment_id = segment.segment_id

        # Create an API request
        auth_url = "https://www.strava.com/api/v3/segments/" + str(segment_id)
        header = {'Authorization':"Bearer " + str(token)}

        # Get API request
        response = requests.get(auth_url, headers=header)

        # Extract segment info from api request
        time=response.json()["athlete_segment_stats"]["pr_elapsed_time"]

        # Create the formated time
        if time is None:
            time = 0
            formated_time = "No Time"

        elif time < 60.0:
            formated_time = str(time) + " s"

        elif time < 3600.0:
            minutes = math.floor(time/60)
            seconds = time - minutes*60
            formated_time = str(minutes) + " min " + str(seconds) + " s"
        else:
            hours = math.floor(time/3600)
            minutes = math.floor((time - hours*60)/60)
            seconds = time - hours*3600 - minutes*60
            formated_time = str(hours) + " hrs " + str(minutes) + " min " + str(seconds) + " s"

        # Update the performance
        performance.time = time
        performance.formated_time = formated_time

        performance.save()

