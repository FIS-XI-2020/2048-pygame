from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from mainwebsite.models import leaderboard

# Default users (username - password):
# admin - qwertyarea51
# hackerman - lmao123
# noobmaster - noob6969ma5ter
def log_in(request):
    ''' Logs a user in based on the POST request.
        Returns False if the credentials are incorrect otherwise True '''
    uname, password = request.POST['username'], request.POST['password']
    user = authenticate(username=uname, password=password)
    if user is not None:
        login(request, user)
        return True

    return False

def register(request):
    ''' Register a new user based on the POST request
    Return codes:
        0: The user has been registered succesfully
        1: Entered passwords do not match
        2: The username already exists
    '''
    print(request.POST)
    uname = request.POST['reg_username']
    password = request.POST['reg_pass']
    confirm_pass = request.POST['confirm_pass']

    if password != confirm_pass: return 1

    try: user = User.objects.create_user(username=uname, password=password)
    except IntegrityError: return 2

    return 0

def logoutpage(request):
    ''' Page for logging out '''
    logout(request)
    return render(request, 'result.html',
                  {'msg':'Logged out succesfully. Goodbye!', 'title':'SUCCESS!'})

def loginpage(request):
    ''' The login/register page view; uses the login() and regiser() functions '''
    if request.method == "POST":
        if 'reg_username' in request.POST:
            # a new user is being registered
            result = register(request)
            if result == 1:
                return render(request, 'incorrect.html',
                              {'msg':'Entered passwords do not match!', 'title':'ERROR!'})
            elif result == 2:
                return render(request, 'incorrect.html',
                              {'msg':'Username already exists! Try another one or login', 'title':'ERROR!'})
            else:
                return render(request, 'result.html',
                              {'msg':'User created succesfully! Go back and login', 'title':'SUCCESS!'})
        else:
            # the user is trying to log in, lets proceed
            if log_in(request):
                with open("authinfo.txt", "w+") as authinfo:
                    authinfo.write(request.POST['username'])
                return render(request, 'result.html',
                              {'msg':'Logged in succesfully! Redirecting to game ...', 'title':'SUCCESS!'})
            else: return render(request, 'incorrect.html',
                                {'msg':'Incorrect credentials!', 'title':'ERROR!'})

    return render(request, 'login.html')

def leaderboardpage(request):
    ''' The leaderboard page view. Displays the rank, username, top
        score and total number of times the user has played, in the
        descending order of top score and scending order of total played '''
    entries = leaderboard.objects.order_by('-top_score', 'total_played').all()
    entries_iterable = zip(entries, range(1, len(entries) + 1))
    return render(request, 'leaderboard.html', {'leaderboard':entries_iterable})
