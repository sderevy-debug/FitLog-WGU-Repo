import calendar
import json
from datetime import date, timedelta

from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from psycopg.types import none

from database.models import DayWorkout, WorkoutPlan, Exercise, Workout


# Pages
@login_required(login_url='/login')
def home(request):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    workouts_this_week = DayWorkout.objects.filter(
        user=request.user,
        date__gte=week_start,
        workout_completed=True
    ).count()

    total_workouts = DayWorkout.objects.filter(
        user=request.user,
        workout_completed=True
    ).count()

    active_plan = WorkoutPlan.objects.filter(
        user=request.user
    ).last()

    recent_activity = DayWorkout.objects.filter(
        user=request.user
    ).select_related('workout', 'workout__plan').order_by('-date')[:10]

    todays_workouts = DayWorkout.objects.filter(
        user=request.user,
        date=today
    ).select_related('workout')

    context = {
        'streak':            request.user.streak,
        'workouts_this_week': workouts_this_week,
        'total_workouts':    total_workouts,
        'active_plan':       active_plan,
        'recent_activity':   recent_activity,
        'todays_workouts':   todays_workouts,
    }
    return render(request, 'dashboard.html', context)

@login_required(login_url='/login')
def about(request):
    context = {}
    return render(request,'about.html',context)

@login_required(login_url='/login')
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
                day_date = date(year, month, day_num)
                calendar_days.append({
                    'blank': False,
                    'number': day_num,
                    'date': day_date,
                    'is_today': day_date == today,
                    'has_workouts': len(day_dws) > 0,
                    'all_complete': bool(day_dws) and all(dw.workout_completed for dw in day_dws),
                    'day_workouts': day_dws,
                    'day_workout_ids': ','.join(str(dw.id) for dw in day_dws),
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
        'workout_plans': WorkoutPlan.objects.filter(user=request.user).prefetch_related('workouts'),
    }
    return render(request,'calendar.html',context)

@login_required(login_url='/login')
def account(request):
    context = {}
    return render(request,'account.html',context)

@login_required(login_url='/login')
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
    return HttpResponseRedirect('/')

def account_register(request):
    if request.method == 'POST':
        User = get_user_model()
        username  = request.POST.get('username')
        email     = request.POST.get('email', '')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return render(request, 'signup.html', {'error': 'Passwords do not match.'})
        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already taken.'})

        user = User.objects.create_user(username=username, email=email, password=password1)
        auth.login(request, user)
        return HttpResponseRedirect('/')

    return render(request, 'signup.html', {})
def account_update(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        user = request.user

        if action == 'profile':
            user.first_name = request.POST.get('first_name', '')
            user.last_name  = request.POST.get('last_name', '')
            user.email      = request.POST.get('email', '')
            user.save(update_fields=['first_name', 'last_name', 'email'])

        elif action == 'password':
            current  = request.POST.get('current_password')
            new      = request.POST.get('new_password')
            confirm  = request.POST.get('confirm_password')
            if user.check_password(current) and new == confirm:
                user.set_password(new)
                user.save(update_fields=['password'])
                auth.login(request, user)

        elif action == 'preferences':
            user.units = request.POST.get('units', 'kg')
            user.save(update_fields=['units'])

        return HttpResponseRedirect('/account')
    return HttpResponseRedirect('/')
def account_delete(request):
    if request.method == 'POST':
        user = request.user
        auth.logout(request)
        user.delete()
        return HttpResponseRedirect('/login')
    return HttpResponseRedirect('/')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(request, username=username, password=password)
        if user:
            auth.login(request, user)
            return HttpResponseRedirect('/home')
        return render(request, 'login.html', {'form': {'errors': True}})
    return render(request, 'login.html', {})

# Database
def plan_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        days_per_week_in = request.POST.get('days')
        description = request.POST.get('desc', '')
        WorkoutPlan.objects.create(user=request.user, name=name, description=description, days_per_week=days_per_week_in)
        return HttpResponseRedirect('/workouts')
    return HttpResponseRedirect('/workouts')

def plan_delete(request, plan_id):
    plan = get_object_or_404(WorkoutPlan, id=plan_id, user=request.user)
    if request.method == 'POST':
        plan.delete()
    return HttpResponseRedirect('/workouts')

def workout_create(request):
    if request.method == 'POST':
        plan = get_object_or_404(WorkoutPlan, id=request.POST.get('plan_id'), user=request.user)

        workout = Workout.objects.create(
            plan=plan,
            name=request.POST.get('workout_name'),
            goal=request.POST.get('goal', '')
        )

        update_exercises(request, workout)

        return HttpResponseRedirect('/workouts')
    return HttpResponseRedirect('/workouts')

def workout_exercises(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, plan__user=request.user)
    exercises = list(workout.exercises.values(
        'id', 'name', 'weight', 'repetitions','sets', 'rest_time', 'intensity'
    ))
    return JsonResponse(exercises, safe=False)

def workout_edit(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, plan__user=request.user)
    if request.method == 'POST':
        workout.name = request.POST.get('workout_name')
        workout.goal = request.POST.get('goal', '')
        workout.save(update_fields=['name', 'goal'])

        workout.exercises.all().delete()

        update_exercises(request, workout)

        return HttpResponseRedirect('/workouts')
    return HttpResponseRedirect('/workouts')

def workout_delete(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, plan__user=request.user)
    if request.method == 'POST':
        workout.delete()
        return HttpResponseRedirect('/workouts')
    return HttpResponseRedirect('/workouts')

def update_exercises(request,workout):
    names = request.POST.getlist('exercise_name[]')
    weights = request.POST.getlist('exercise_weight[]')
    reps = request.POST.getlist('exercise_reps[]')
    sets = request.POST.getlist('exercise_sets[]')
    rest = request.POST.getlist('exercise_rest[]')
    intensities = request.POST.getlist('exercise_intensity[]')

    for i, name in enumerate(names):
        if not name.strip():
            continue
        Exercise.objects.create(
            workout=workout,
            name=name.strip(),
            weight=weights[i] or 0,
            repetitions=reps[i] or None,
            sets=sets[i] or None,
            rest_time=rest[i] or '1:00',
            intensity=intensities[i],
            superset=False,
        )

def assign_workout(request):
    if request.method == 'POST':
        workout_id = request.POST.get('workout_id')
        date       = request.POST.get('date').format()
        if workout_id and date:
            workout = get_object_or_404(Workout, id=workout_id, plan__user=request.user)
            DayWorkout.objects.get_or_create(
                user=request.user,
                workout=workout,
                date=date,
                defaults={'workout_completed': False}
            )
        return HttpResponseRedirect('/calendar')
    return HttpResponseRedirect('/calendar')

def day_workouts_json(request):
    date = request.GET.get('date')
    workouts = DayWorkout.objects.filter(
        user=request.user, date=date
    ).select_related('workout')
    data = [{'id': dw.id, 'name': dw.workout.name} for dw in workouts]
    return JsonResponse(data, safe=False)

def remove_workout(request, day_workout_id):
    dw = get_object_or_404(DayWorkout, id=day_workout_id, user=request.user)
    if request.method == 'POST':
        dw.delete()
    return HttpResponseRedirect('/calendar')

def plan_export(request, plan_id):
    plan = get_object_or_404(WorkoutPlan, id=plan_id, user=request.user)
    data = {
        'name':         plan.name,
        'description':  plan.description,
        'days_per_week': plan.days_per_week,
        'workouts': []
    }
    for workout in plan.workouts.all():
        workout_data = {
            'name': workout.name,
            'goal': workout.goal,
            'exercises': []
        }
        for ex in workout.exercises.all():
            workout_data['exercises'].append({
                'name':        ex.name,
                'weight':      ex.weight,
                'repetitions': ex.repetitions,
                'rest_time':   str(ex.rest_time),
                'sets':        ex.sets,
                'intensity':   ex.intensity,
                'superset':    ex.superset,
                'description': ex.description,
            })
        data['workouts'].append(workout_data)

    response = JsonResponse(data)
    response['Content-Disposition'] = f'attachment; filename="{plan.name}.json"'
    return response

def plan_import(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            plan = WorkoutPlan.objects.create(
                user=request.user,
                name=data['name'],
                description=data.get('description', ''),
                days_per_week=data.get('days_per_week', 1),
            )
            for workout_data in data.get('workouts', []):
                workout = Workout.objects.create(
                    plan=plan,
                    name=workout_data['name'],
                    goal=workout_data.get('goal', ''),
                )
                for ex in workout_data.get('exercises', []):
                    Exercise.objects.create(
                        workout=workout,
                        name=ex['name'],
                        weight=ex.get('weight', 0),
                        repetitions=ex.get('repetitions'),
                        rest_time=ex.get('rest_time', '00:00:00'),
                        sets=ex.get('sets', 1),
                        intensity=ex.get('intensity', 'ME'),
                        superset=ex.get('superset', False),
                        description=ex.get('description', ''),
                    )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid method'})

def toggle_workout_complete(request,day_workout_id):
    if request.method == 'POST':
        day_workout = DayWorkout.objects.get(pk=day_workout_id, user=request.user)
        day_workout.workout_completed = not day_workout.workout_completed
        day_workout.save()
        return HttpResponseRedirect('/calendar')
    return HttpResponseRedirect('/')