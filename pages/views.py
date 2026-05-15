import calendar
from datetime import date

from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from database.models import DayWorkout, WorkoutPlan


# Pages
def home(request):
    context = {}
    return render(request, 'dashboard.html', context)
def about(request):
    context = {}
    return render(request,'about.html',context)
def calendar_page(request):
    today = date.today()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    cal = calendar.monthcalendar(year, month)

    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    day_workouts = DayWorkout.objects.filter(
        user=request.user,
        date__year=year,
        date__month=month
    ).select_related('workout')

    dw_by_day = {}
    for dw in day_workouts:
        dw_by_day.setdefault(dw.date.day, []).append(dw)

    calendar_days = []
    for week in cal:
        for day_num in week:
            if day_num == 0:
                calendar_days.append({'blank': True})
            else:
                day_dws = dw_by_day.get(day_num, [])
                calendar_days.append({
                    'blank': False,
                    'number': day_num,
                    'is_today': day_num == today.day and month == today.month and year == today.year,
                    'all_complete': bool(day_dws) and all(dw.workout_completed for dw in day_dws),
                    'day_workouts': day_dws,
                })

    context = {
        'month_name': calendar.month_name[month],
        'year': year,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'day_labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'calendar_days': calendar_days,
    }
    return render(request,'calendar.html',context)
def account(request):
    context = {}
    return render(request,'account.html',context)
def workouts(request):
    context = {'workout_plans': WorkoutPlan.objects.filter(user=request.user)}
    return render(request,'workouts.html',context)
def login(request):
    context = {}
    return render(request,'login.html',context)

# Actions
def account_logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return render(request, 'login.html')

    else:
        return HttpResponseRedirect('/')
def account_register(request):
    if request.method == 'POST':
        return HttpResponse('Registered')
    else:
        return HttpResponseRedirect('/')
def account_update(request):
    if request.method == 'POST':
        return HttpResponse('Updated')
    else:
        return HttpResponseRedirect('/')
def account_delete(request):
    if request.method == 'POST':
        return HttpResponse('Deleted')
    else:
        return HttpResponseRedirect('/')

# Database
def plan_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        num_per_week = request.POST.get('num_per_week', 0)
        WorkoutPlan.objects.create(user=request.user, name=name, description=description, days_per_week=num_per_week)
        return HttpResponseRedirect('/workouts')
    return HttpResponseRedirect('/workouts')

def toggle_workout_complete(request,day_workout_id):
    if request.method == 'POST':
        day_workout = DayWorkout.objects.get(pk=day_workout_id)
        day_workout.workout_completed = not day_workout.workout_completed
        day_workout.save()
        return HttpResponseRedirect('/calendar')
    else:
        pass