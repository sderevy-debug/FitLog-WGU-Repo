from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q

class CustomUser(AbstractUser):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    workout_plans = models.ForeignKey('WorkoutPlan',on_delete=models.CASCADE, null=True, blank=True)

class WorkoutPlan(models.Model):
    name = models.CharField(max_length=100)
    days_per_week = models.IntegerField(default=1)
    description = models.TextField(default='No description')
    workouts = models.ForeignKey('Workout', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return (f'Name: {self.name} - ',
                f'Days Per Week: {self.days_per_week} - ',
                f'Workout: {self.workouts}')

class Workout(models.Model):
    name = models.CharField(max_length=100)
    goal = models.TextField(default='No goal')
    exercises = models.ForeignKey('Exercise',on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return (f'Name: {self.name} - '
                f'Goal: {self.goal} - ')

class Exercise(models.Model):
    name = models.CharField(max_length=100)
    movement_type = models.CharField(max_length=100,blank=True, null=True)
    weight = models.IntegerField()
    rest_time = models.TimeField()
    superset = models.BooleanField()
    description = models.TextField(default='No description')
    intensity_levels = {
        'LO':'Light',
        'ME':'Moderate',
        'HI':'Vigorous',
        'EX':'Deadly'
    }
    intensity = models.CharField(choices=intensity_levels,default='ME',max_length=2)
    repetitions = models.IntegerField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(Q(repetitions__isnull=False) & Q(time__isnull=True) |
                       Q(repetitions__isnull=True) & Q(time__isnull=False)
                ),
                name='Either repetitions or time'
            )
        ]

    def __str__(self):
        return (f'Name: {self.name} - ',
                f'Description: {self.description} - ',
                f'Intensity: {self.intensity}')

class DayWorkout(models.Model):
    workout = models.ForeignKey(Workout,on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    workout_completed = models.BooleanField(default=False)
    notes = models.TextField(default='No notes')

    def __str__(self):
        return (f'Date: {self.date} - ',
                f'Workout: {self.workout.name}'
                f'Completed: {self.workout_completed}')