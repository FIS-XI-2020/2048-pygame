from django.shortcuts import render

# Create your views here.
default_users: {'admin':'qwertyarea51'}

#def login(uname, pass):

def loginpage(request):
    return render(request, "login.html")
