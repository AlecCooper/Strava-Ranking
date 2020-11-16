from django.contrib import admin
from .models import Ranking, Segment, Performance

# Register your models here.
admin.site.register(Ranking)
admin.site.register(Segment)
admin.site.register(Performance)