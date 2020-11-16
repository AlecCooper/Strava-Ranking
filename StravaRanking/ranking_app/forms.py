from django import forms 
from django.contrib.auth.models import User

from .models import Ranking
from .validators import validate_username, validate_segment, validate_ranking

class createRankingForm(forms.Form):

    name = forms.CharField(max_length=50, required=True, validators=[validate_ranking])

class rankingForm(forms.Form):

    segment_url = forms.URLField(max_length=200, required=False, validators=[validate_segment])
    add_user = forms.CharField(max_length=150, required=False, validators=[validate_username])


