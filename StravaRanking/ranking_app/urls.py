from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('logout', views.logout_page, name='logout'),
    path('create', views.create_ranking, name='ranking'),
    path('<str:ranking_name>', views.ranking),
    path('<str:ranking_name>/edit', views.edit_ranking),
    path('<str:ranking_name>/segments/<str:segment_name>', views.segment),
    path('<str:ranking_name>/profiles/<str:profile_name>', views.profile)
]
