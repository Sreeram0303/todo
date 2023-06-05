from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from django.db import IntegrityError
from .models import TODO
from django.utils import timezone
from django.contrib.auth.decorators import login_required
# Create your views here.


def home(request):
    return render(request, 'todo\home.html')


def signupuser(request):
    if request.method == 'GET':
        return render(request, 'todo\signupuser.html', {'form': UserCreationForm})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, 'todo\signupuser.html', {'form': UserCreationForm, 'error': "User already exist.Choose any other usernames"})
        else:
            return render(request, 'todo\signupuser.html', {'form': UserCreationForm, 'error': "passwords doesn't match"})


def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todo\loginuser.html', {'form': AuthenticationForm})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo\loginuser.html', {'form': AuthenticationForm, 'error': "username and password doesn't match"})
        else:
            login(request, user)
            return redirect('currenttodos')

@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'todo\createtodo.html', {'form': TodoForm})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo\createtodo.html', {'form': TodoForm, 'error': "Try again! Bad data passed in"})

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect("home")
@login_required
def viewtodo(request,todo_pk):
    todo = get_object_or_404(TODO,pk = todo_pk,user = request.user)
    if request.method == "GET":
        form = TodoForm(instance=todo)
        return render(request,'todo/viewtodo.html',{'todo':todo,'form':form})
    else:
        try:
            form = TodoForm(request.POST,instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request,'todo/viewtodo.html',{'todo':todo,'form':form,'error':"Bad data!"})
@login_required
def completetodo(request,todo_pk):
    todo = get_object_or_404(TODO,pk = todo_pk,user = request.user)
    if request.method == "POST":
        todo.completed = timezone.now()
        todo.save()
        return redirect('currenttodos')
@login_required    
def deletetodo(request,todo_pk):
    todo = get_object_or_404(TODO,pk = todo_pk,user = request.user)
    if request.method == "POST":
        todo.delete()
        return redirect('currenttodos')

@login_required
def currenttodos(request):
    todos = TODO.objects.filter(user=request.user, completed__isnull=True)
    return render(request, 'todo\currenttodo.html', {'todos': todos})
@login_required
def completedtodos(request):
    todos = TODO.objects.filter(user=request.user, completed__isnull=False).order_by('completed')
    return render(request, 'todo\completedtodo.html', {'todos': todos})