from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
import requests

from .models import Ranking


def validate_ranking(name):

    if Ranking.objects.filter(name=name).exists():
        raise ValidationError("Ranking name already exists. Try again")

def validate_username(username):

    if not User.objects.filter(username=username):
        raise ValidationError("User does not exist. Try again")

    return username

def validate_segment(url):

    id_index = url.find('strava.com/segments/') 

    if id_index == -1:
        raise ValidationError("Enter a valid segment URL")
    
    else:
        segment_id = url[id_index + 20:]

    # Make sure segment id is a integer
    try:
        segment_id = int(segment_id)
    except:
        raise ValidationError("Enter a valid segment URL")

    # See if the url raises a 404 error
    response = requests.get(url)

    if(response.status_code == 404):
        raise ValidationError("Enter a valid segment URL")

    # Check if redirects to search page
    if response.url != url:
        raise ValidationError("Enter a valid segment URL")
        
    return url