from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse

def get_dealerships(request):
    context = {}
    if request.user.is_authenticated:
        context['username'] = request.user.username
    return render(request, 'djangoapp/index.html', context)

def about(request):
    context = {}
    return render(request, 'djangoapp/about.html', context)

def contact(request):
    context = {}
    return render(request, 'djangoapp/contact.html', context)

def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        email = request.POST['email']
        
        username_exist = False
        email_exist = False
        try:
            User.objects.get(username=username)
            username_exist = True
        except:
            pass
        
        if not username_exist:
            user = User.objects.create_user(username=username, first_name=first_name, 
                                          last_name=last_name, password=password, email=email)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists"
            return render(request, 'djangoapp/registration.html', context)
