from django.urls import path
from . import views,ai_views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('ai/', ai_views.db_agent_view, name='db_agent'),
]
