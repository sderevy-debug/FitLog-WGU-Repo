"""
URL configuration for fitlog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from pages import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('workouts/', views.workouts, name='workouts'),
    path('account/', views.account, name='account'),
    path('calendar/', views.calendar_page, name='calendar'),
    path('login/', views.login, name='login'),
    path('', RedirectView.as_view(url='/login/'), name='home-redirect'),
    path('signup/', views.account_register, name='account_register'),

    path('account_register/', views.account_register, name='account_register'),
    path('account_logout/', views.account_logout, name='account_logout'),
    path('account_update/', views.account_update, name='account_update'),
    path('account_delete/', views.account_delete, name='account_delete'),

    path('plan_create/', views.plan_create, name='plan_create'),
    path('plan/<int:plan_id>/delete/', views.plan_delete, name='plan_delete'),

    path('workout_create/', views.workout_create, name='workout_create'),
    path('workout_edit/<int:workout_id>/', views.workout_edit, name='workout_edit'),
    path('workout_delete/<int:workout_id>/', views.workout_delete, name='workout_delete'),
    path('workout_exercises/<int:workout_id>/', views.workout_exercises, name='workout_exercises'),

    path('calendar/assign/', views.assign_workout, name='assign_workout'),
    path('calendar/day_workouts/', views.day_workouts_json, name='day_workouts_json'),
    path('calendar/remove_workout/<int:day_workout_id>/', views.remove_workout, name='remove_workout'),

    path('workouts/plan/<int:plan_id>/export/', views.plan_export, name='plan_export'),
    path('workouts/import/', views.plan_import, name='plan_import'),

    path('toggle_workout_complete/<int:day_workout_id>/', views.toggle_workout_complete, name='toggle_workout_complete'),

    # Password reset
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset/password_reset_complete.html'), name='password_reset_complete'),
]
