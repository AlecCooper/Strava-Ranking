import requests
import datetime
from allauth.socialaccount.models import SocialToken, SocialApp
from django.utils import timezone

def refresh_token(user):

    # Get the social token
    token = SocialToken.objects.get(account__user=user, account__provider='strava')

    # Determine if the token is expired, if so get a new one
    if token.expires_at < timezone.now():

        # Get the client ID and secret
        app = SocialApp.objects.get(name="Strava API")
        client_id = app.client_id
        client_secret = app.secret

        # Get the refresh token
        refresh_token = token.token_secret

        # Create an API request
        auth_url = "https://www.strava.com/oauth/token"

        payload = {
            'client_id':client_id,
            'client_secret':client_secret,
            'grant_type':'refresh_token',
            'refresh_token':refresh_token
            }

        response = requests.post(auth_url, params=payload).json()

        # Convert epoch time to datetime
        expires_at = datetime.datetime.fromtimestamp(response["expires_at"])

        # Save the new token
        token.token = response["access_token"]
        token.token_secret = response["refresh_token"]
        token.expires_at = expires_at

        token.save()

        return token

    # We don't need to request a new token
    else:
        return token

