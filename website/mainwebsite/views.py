from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

# Create your views here.
default_users: {'admin':'qwertyarea51'}

def login(request):
    uname, password = request.POST['username'], request.POST['password']
    user = authenticate(username=uname, password=password)
    if user is not None:
        login(request, user)
        return True

    return False

def register(request):
    uname = request.POST['reg_username']
    password = request.POST['password']
    confirm_pass = request.POST['confirm_pass']

    if password != confirm_pass:
        return render(request, 'result.html', {'msg':'Entered passwords do not match!', 'title':'ERROR!'})

    user = User.objects.create_user(username=uname, password=password)
    return render(request, 'result.html', {'msg':'User created succesfully!', 'title':'SUCCESS!'})

def loginpage(request):
    if request.method == "POST":
        if 'reg_username' in request.POST: register(request)
        else:
            result = login(request)
            if result: return render(request, 'result.html', {'msg':'Logged in succesfully!', 'title':'SUCCESS!'})
            else: return render(request, 'result.html', {'msg':'Incorrect credentials!', 'title':'ERROR!'})

    return render(request, 'login.html')
