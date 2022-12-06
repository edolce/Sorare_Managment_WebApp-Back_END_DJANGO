from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('getPlayersAverage/', views.getPlayersAverage, name='getPlayersAverage'),
    path('getExtraPlayerData/', views.getExtraPlayerData, name='getExtraPlayerData'),
    # Update all bundle datas in database and retrieve them to front-end
    path('init/', views.initData, name='initData')
]