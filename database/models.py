from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q

class CustomUser(AbstractUser):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    streak = models.IntegerField(default=0)
    last_streak_update = models.DateField(null=True, blank=True)
    units = models.CharField(max_length=3, default='kg', choices={'kg': 'Kilograms', 'lbs': 'Pounds'})

class WorkoutPlan(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='workout_plans')
    name = models.CharField(max_length=100)
    days_per_week = models.IntegerField(default=1)
    description = models.TextField(default='No description')

class Workout(models.Model):
    plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name='workouts')
    name = models.CharField(max_length=100)
    goal = models.TextField(default='No goal')

class Exercise(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='exercises')
    name = models.CharField(max_length=100)
    movement_type = models.CharField(max_length=100, blank=True, null=True)
    weight = models.IntegerField()
    rest_time = models.TimeField()
    sets = models.IntegerField()
    superset = models.BooleanField()
    description = models.TextField(default='No description')
    intensity_levels = {
        'LO': 'Light',
        'ME': 'Moderate',
        'HI': 'Vigorous',
        'EX': 'Deadly'
    }
    intensity = models.CharField(choices=intensity_levels, default='ME', max_length=2)
    repetitions = models.IntegerField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(Q(repetitions__isnull=False) & Q(time__isnull=True) |
                           Q(repetitions__isnull=True) & Q(time__isnull=False)),
                name='Either repetitions or time'
            )
        ]

class DayWorkout(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='day_workouts')
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    date = models.DateField()
    workout_completed = models.BooleanField(default=False)
    notes = models.TextField(default='No notes')