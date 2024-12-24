from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from .models import UserModel

existing_list_header = "Please enter the password to access the To Do List"

def startup(request):
    # Check if this is the first-time setup
    if User.objects.count() == 0:
        # New instance, prompt user to create password
        request.session['is_init'] = True
        return render(request, "ToDoList/signup.html", {
            "list_header": "Please create a password for future access to To Do List",
            "hint_support": "Please enter a hint to help you recollect the password",
        })
    else:
        # Existing instance, prompt for login
        return render(request, "ToDoList/login.html", {
            "list_header": existing_list_header,
        })

def user_login(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Route not supported")
    
    pwd = request.POST.get("password")
    hint = request.POST.get("hint")
    is_init = request.session.get('is_init', False)
    
    if is_init:
        # Initialize the password
        if not pwd or not hint:
            return render(request, "ToDoList/signup.html", {
                "aux_message": "Password and hint can't be empty, please try again.",
                "list_header": "Please create a password for future access to To Do List",
                "hint_support": "Please enter a hint to help you recollect the password",
            })

        # Create admin user and store hint
        user = User.objects.create_user(username="admin", password=pwd)
        UserModel.objects.create(user=user, hint=hint)
        request.session['is_init'] = False
        return render(request, "ToDoList/login.html", {
            "aux_message": "Password created successfully. Please log in.",
            "list_header": existing_list_header,
        })
    else:
        # Authenticate user
        user = authenticate(request, username="admin", password=pwd)
        if user is not None:
            login(request, user)
            request.session['login_attempt_counter'] = 0  # Reset counter
            return HttpResponseRedirect(reverse("list"))
        else:
            # Handle failed login attempts
            counter = request.session.get('login_attempt_counter', 0) + 1
            request.session['login_attempt_counter'] = counter

            if counter > 3:
                hint = UserModel.objects.filter(user__username="admin").first().hint
                return render(request, "ToDoList/login.html", {
                    "aux_message": f"Hint: {hint}",
                    "list_header": existing_list_header,
                })
            else:
                return render(request, "ToDoList/login.html", {
                    "aux_message": "Invalid password. Please try again.",
                    "list_header": existing_list_header,
                })
