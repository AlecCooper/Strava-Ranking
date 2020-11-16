from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
import requests
from allauth.socialaccount.models import SocialToken, SocialAccount
from .strava import refresh_token
import math
    
# Create your models here.
class Ranking(models.Model):

    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta():
       permissions = [('member','Is a member of the ranking')]

    def get_absolute_url(self):
        return str(self.name).replace(" ", "%20")

    def get_ranking(self):
        
        # Get all users in the ranking
        users = User.objects.filter(groups__name=self.name)
        segments = Segment.objects.filter(ranking=self)
        
        # Lambda func for accessesing sort criteria in segment_list
        sort_key = lambda x: x[1]
        
        ranked_segments = []

        # Loop through each segment
        for segment in segments:
            segment_list = []

            # Get performance of each user
            for user in users:

                # We must create a performance if one does not exist
                if Performance.objects.filter(owner=user, segment=segment).exists():
                    performance = Performance.objects.get(owner=user, segment=segment)
                else:
                    performance = Performance.create(user, segment)
                    performance.save()

                # If the user has a time of 0, we change to float(inf)
                # for comparison purposes
                if (performance.time == 0.0):
                    time = float("inf")
                else:
                    time = performance.time

                segment_list.append((user, time))

            # Sort position by time
            segment_list.sort(key=sort_key)

            segment_indexed_list = []

            # If all are 0, there is no ranking
            if segment_list[0][1] == float("inf"):
                for segment in segment_list:
                    segment_indexed_list.append([segment[0], 0])

            else:
                # Turn times into indices
                index = 1
                prev_time = segment_list[0]
                for tup in segment_list:
                    user = tup[0]
                    if tup[1] == prev_time:
                        segment_indexed_list.append([user, index])
                    else:
                        prev_time = tup[1]
                        segment_indexed_list.append([user, index])
                        index += 1

            ranked_segments.append(segment_indexed_list)

        ranked = []

        # Add up the positions 
        for user in users:
            user_score = 0
            for segment_indexed_list in ranked_segments:
                for tup in segment_indexed_list:
                    if (user.username == tup[0].username):
                        user_score += tup[1]
            ranked.append((user,user_score))

        ranked.sort(key=sort_key)

        # Turn positions into rankings
        rank = 1
        i = 0 
        current_pos = ranked[0][1]
        for ranking in ranked:
            if ranking[1] == current_pos:
                ranked[i] = (ranking[0], rank)
            else:
                rank += 1
                current_pos = ranked[i][1]
                ranked[i] = (ranking[0], rank)
            i += 1  

        # Get user's social profile
        for i in range(0, len(ranked)):
            account = SocialAccount.objects.get(user=ranked[i][0])
            extra_data = account.extra_data
            first_name = extra_data["firstname"]
            last_name = extra_data["lastname"]
            ranked[i] = [ranked[i][0],ranked[i][1],first_name,last_name]

        return ranked

class Segment(models.Model):

    ranking = models.ForeignKey("ranking_app.Ranking", on_delete=models.CASCADE)
    url = models.URLField(max_length=200)
    segment_id=models.IntegerField(null=True)
    name = models.CharField(max_length=50)
    distance = models.FloatField(null=True)
    formated_distance = models.CharField(null=True,max_length=50)

    def get_absolute_url(self):
        
        url = self.ranking.get_absolute_url()
        url += "/segments/"
        url += self.name.replace(" ", "%20")

        return url
            
    # Formats the distance to a string of km/m
    def format_distance(distance):

        # Display in m
        if distance < 1000:
            distance = int(distance)
            return str(distance) + " m"

        # Display in km
        else:
            distance = distance/1000

            return "{:.2f} km".format(distance)

    @classmethod
    def create(cls, url, ranking, request):

        segment_id = url[url.find('strava.com/segments/') + 20:]

        # Get the social token
        token = SocialToken.objects.get(account__user=request.user, account__provider='strava')

        # Refresh token
        token = refresh_token(request.user)

        # Create an API request
        auth_url = "https://www.strava.com/api/v3/segments/" + str(segment_id)
        header = {'Authorization':"Bearer " + str(token)}

        # Get API request
        response = requests.get(auth_url, headers=header)

        # Extract segment info from api request
        name=response.json()['name']
        distance = response.json()['distance']

        formated_distance = cls.format_distance(distance)

        segment = cls(ranking=ranking, name=name, url=url, segment_id=segment_id, distance=distance,formated_distance=formated_distance)

        return segment

    def get_ranking(self):

        ranking = self.ranking

        # Get all users in the ranking
        users = User.objects.filter(groups__name=ranking.name)

        # Get each performance
        performances = []
        for user in users:

            # We must create a performance if one does not exist
            if Performance.objects.filter(owner=user, segment=self).exists():
                performance = Performance.objects.get(owner=user, segment=self)
            else:
                performance = Performance.create(user, self)
                performance.save()

            # If the user has a time of 0, we change to float(inf)
            # for comparison purposes
            if (performance.time == 0.0):
                time = float("inf")
            else:
                time = performance.time

            performances.append((performance.owner.username, time, performance.formated_time))

        sort_key = lambda x: x[1]
        # Sort position by time
        performances.sort(key=sort_key)
        
        # Add in positions
        pos = 1
        prev_time = performances[0][1]
        # If nobody has a time there is no ranking
        if prev_time == float("inf"):

            for i in range(0, len(performances)):
                performances[i] = (performances[i][0], "No Time", 0, "No Time")

        else:

            for i in range(0, len(performances)):
                
                # If same time, share position
                if performances[i][1] == prev_time:
                    performances[i] = (performances[i][0], performances[i][1], pos, performances[i][2])
                
                else:
                    pos += 1
                    prev_time = performances[i][1]
                    performances[i] = (performances[i][0], performances[i][1], pos, performances[i][2])


        # Remove infs
        i = 0
        for performance in performances:
            if performance[1] == float("inf"):
                performances[i] = (performance[0], "No Time", performance[2], performance[3])
            i+=1

        # Add in user firstname/lastname
        for i in range(len(performances)):

            account = SocialAccount.objects.get(user__username=performances[i][0])
            extra_data = account.extra_data
            first_name = extra_data["firstname"]
            last_name = extra_data["lastname"]

            performances[i] = (
                performances[i][0], 
                "No Time", 
                performances[i][2], 
                performances[i][3], 
                first_name, 
                last_name
                )

        return performances

class Performance(models.Model):

    segment = models.ForeignKey("ranking_app.Segment", on_delete=models.CASCADE)
    ranking = models.ForeignKey("ranking_app.Ranking", on_delete=models.CASCADE)
    #activity_url = models.URLField(max_length=200)
    owner = models.ForeignKey(User,verbose_name = 'User', on_delete=models.CASCADE)
    time = models.FloatField(null=True)
    formated_time = models.CharField(null=True, max_length=50)

    @classmethod
    def create(cls, user, segment):

        ranking=segment.ranking
        segment_id = segment.segment_id

        # Get the social token
        token = SocialToken.objects.get(account__user=user, account__provider='strava')

        # Refresh token
        token = refresh_token(user)

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

        preformance = cls(owner=user, segment=segment, ranking=ranking, time=time, formated_time=formated_time)

        return preformance

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Gets all the segments for the current ranking
    def get_segments(self, ranking):

        performances = Performance.objects.filter(ranking=ranking, owner=self.user)

        # list of performances with rank
        ranked_perf = []

        for performance in performances:

            segment = performance.segment
            ranks = segment.get_ranking()

            for rank in ranks:
                if rank[0] == self.user.username:
                    # If position is 0, we replace it with "NA"
                    if rank[2] == 0:
                        ranked_perf.append([segment, rank[3], segment.formated_distance, "NA"])
                    else:
                        ranked_perf.append([segment, rank[3], segment.formated_distance, rank[2]])

        return ranked_perf


    


    