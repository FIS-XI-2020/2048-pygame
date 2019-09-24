from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from mainwebsite.models import leaderboard

# Create your views here.

# Default users (username - password):
# admin - qwertyarea51
# hackerman - lmao123
def log_in(request):
    uname, password = request.POST['username'], request.POST['password']
    user = authenticate(username=uname, password=password)
    if user is not None:
        login(request, user)
        return True

    return False

def register(request):
    print(request.POST)
    uname = request.POST['reg_username']
    password = request.POST['reg_pass']
    confirm_pass = request.POST['confirm_pass']

    if password != confirm_pass: return 1

    try: user = User.objects.create_user(username=uname, password=password)
    except IntegrityError: return 2

    return 0

def logoutpage(request):
    logout(request)
    return render(request, 'result.html', {'msg':'Logged out succesfully!', 'title':'SUCCESS!'})

def loginpage(request):
    if request.method == "POST":
        if 'reg_username' in request.POST:
            result = register(request)
            if result == 1:
                return render(request, 'result.html', {'msg':'Entered passwords do not match!', 'title':'ERROR!'})
            elif result == 2:
                return render(request, 'result.html', {'msg':'Username already exists! Try another one or login', 'title':'ERROR!'})
            else:
                return render(request, 'result.html', {'msg':'User created succesfully!', 'title':'SUCCESS!'})
        else:
            if log_in(request):
                with open("authinfo.txt", "w+") as authinfo:
                    authinfo.write(request.POST['username'])
                return render(request, 'result.html', {'msg':'Logged in succesfully! Redirecting to game ...', 'title':'SUCCESS!'})
            else: return render(request, 'result.html', {'msg':'Incorrect credentials!', 'title':'ERROR!'})

    return render(request, 'login.html')

def leaderboardpage(request):
    entries = leaderboard.objects.order_by('top_score', 'total_played').all()
    entries_iterable = zip(entries, range(1, len(entries) + 1))
    return render(request, 'leaderboard.html', {'leaderboard':entries_iterable})
