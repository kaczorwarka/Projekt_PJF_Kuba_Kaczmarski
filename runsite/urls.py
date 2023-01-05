from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('1.0', views.run_plan, name="run_plan"),
    path('2.0', views.run_plan, name="run_plan"),
    path('3.0', views.run_plan, name="run_plan"),
    path('4.0', views.run_plan, name="run_plan"),
    path('5.0', views.run_plan, name="run_plan"),
]