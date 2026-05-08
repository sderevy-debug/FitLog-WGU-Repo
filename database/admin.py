from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

admin.site.register(CustomUser, UserAdmin)
admin.site.register(Workout)
admin.site.register(WorkoutPlan)
admin.site.register(DayWorkout)
admin.site.register(Exercise)