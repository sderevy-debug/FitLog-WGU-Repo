from django.shortcuts import render

def home(request):
    context = {}
    return render(request, 'home.html', context)

def about(request):
    context = {}
    return render(request,'about.html',context)

def calendar(request):
    context = {}
    return render(request,'calendar.html',context)

def account(request):
    context = {}
    return render(request,'account.html',context)

def workouts(request):
    context = {}
    return render(request,'workouts.html',context)
