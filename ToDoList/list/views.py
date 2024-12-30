from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required
from .models import ListModel
from .forms import *
from datetime import datetime


# Create your views here.
@login_required(login_url='/')
def index(request):
    return render(request, "list/index.html")

@login_required(login_url='/')
def list_view(request):
    return render(request, "list/list_view.html", {
        "content": ListModel.objects.filter(is_complete = False),
        "callback": "list",
        "title": "Current Tasks"
    })

@login_required(login_url='/')
def complete_list_view(request):
    return render(request, "list/list_view.html", {
        "content": ListModel.objects.filter(is_complete = True),
        "title": "Completed Tasks"
    })

@login_required(login_url='/')
def entry_add(request):
    # render 'list' if no callback is provided
    callback = request.GET.get('callback', 'list')
    priority = int(request.GET.get('priority', '0'))
    if request.method == "GET":
        # add a new entry
        return render(request, "list/entry_edit.html", {
            "form": EntryFormBuilder().title().description().priority().due_date().build(),
            "callback": callback,
            "entry_add": True
        })
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority')
        due_date = request.POST.get('due_date')
        if not title or not description or not priority or not due_date:
            return render(request, "list/entry_edit.html", {
                "aux_message": "Any value can't be empty. Please try again.",
                "entry_add": True
            })
        ListModel.objects.create(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            is_complete = False
        )
        if priority == 0:
            return redirect(reverse(callback))
        else:
            return redirect("priority", priority = priority)

    return HttpResponseBadRequest("Invalid request method.")

@login_required(login_url='/')
def entry_edit(request, entry_id):
    entry = ListModel.objects.filter(id=entry_id)
    if not entry:
        return HttpResponseBadRequest("entry doesn't exist")
    entry = entry.first()

    if request.method == 'GET':
        request.session["is_select"] = False
        return render(request, "list/edit_element_select.html", {
            "form": EditSelectForm(),
            "entry": entry
        })

    elif request.method == "POST" and request.session["is_select"] is False:
        edit_select_form = EditSelectForm(request.POST)
        if edit_select_form.is_valid():
            editable_fields = edit_select_form.cleaned_data['choices']
            request.session["is_select"] = True
            return render(request, "list/entry_edit.html", {
                "editable": editable_fields,
                "form": EntryFormBuilder().include_fields(editable_fields).build(),
                "id": entry.id
            })
        else:
            # Error in form, return to the select form with errors
            return render(request, "list/edit_element_select.html", {
                "form": edit_select_form,
                "entry": entry
            })

    elif request.method == "POST" and request.session["is_select"] is True:
        entry.title = request.POST.get('title', entry.title)
        entry.description = request.POST.get('description', entry.description)
        entry.priority = request.POST.get('priority', entry.priority)
        entry.due_date = request.POST.get('due_date', entry.due_date)
        entry.save()
        return redirect("entry", entry_id=entry.id)

@login_required(login_url='/')
def entry(request, entry_id):
    return render(request, "list/entry.html", {
        "entry": ListModel.objects.filter(id = entry_id).first()
    })

@login_required(login_url='/')
def priority_sort(request, priority):
    if priority < 1 or priority > 3:
        return HttpResponseBadRequest("priority can only be between 1 (low) and 3 (high)")
    content = None
    title = None
    if priority == 1:
        content = ListModel.objects.filter(priority = 1, is_complete = False)
        title = "Low Priority Tasks"
    elif priority == 2:
        content = ListModel.objects.filter(priority = 2, is_complete = False)
        title = "Medium Priority Tasks"
    elif priority == 3:
        content = ListModel.objects.filter(priority = 3, is_complete = False)
        title = "High Priority Tasks"
    return render(request, "list/list_view.html", {
        "content": content,
        "callback": "priority",
        "priority": priority,
        "title": title
    })

@login_required(login_url='/')
def date_sort(request):
    if request.method == 'GET':
        return render(request, "list/date_sort_view.html", {
            "msg": "Please select how you want to sort the To Do List",
            "sort_form": DateSelectForm()
        })
    elif request.method == 'POST':
        form = DateSelectForm(request.POST)
        if form.is_valid():
            cleaned_data = form.clean()
            if cleaned_data.get('ascending') is True:
                list_entries = ListModel.objects.order_by('due_date').filter(is_complete = False)
                return render(request, "list/date_sort_view.html", {
                    "msg": "Ascending Sort",
                    "content": list_entries,
                    "sort_form": DateSelectForm()
                })
            elif cleaned_data.get('descending') is True:
                list_entries = ListModel.objects.order_by('-due_date').filter(is_complete = False)
                return render(request, "list/date_sort_view.html", {
                    "msg": "Descending Sort",
                    "content": list_entries,
                    "sort_form": DateSelectForm()
                })
            elif cleaned_data.get('date_sort') is not None:
                list_entries = ListModel.objects.filter(due_date = cleaned_data.get('date_sort')).filter(is_complete = False)
                return render(request, "list/date_sort_view.html", {
                    "msg": f"Sort for {cleaned_data.get('date_sort')}",
                    "content": list_entries,
                    "sort_form": DateSelectForm()
                })
        else:
            return render(request, "list/date_sort_view.html", {
                "msg": "Error",
                "sort_form": form
            })
    return HttpResponseBadRequest("route not supported")

@login_required(login_url='/')
def remove(request, type):
    if request.method == 'GET':
            # display relevant tasks for selection
            title = None
            match type:
                case '3':
                    title = "High Priority"
                case '2': 
                    title = "Medium Priority"
                case '1':
                    title = "Low Priority"
                case 'list':
                    title = "Current Tasks"
                case _:
                    title = type
            return render(request, "list/remove_view.html", {
                'form': RemoveSelectionForm(type = str(type)),
                'type': type,
                'title': title
            })
    elif request.method == 'POST':
        form = RemoveSelectionForm(data=request.POST, type = type)
        if form.is_valid():
            completed_tasks = form.cleaned_data['tasks']
            completed_tasks.update(is_complete = True)
            match type:
                case 'list':
                    return redirect('list')
                case '3' | '2' | '1':
                    return redirect('priority', priority = int(type))
                case 'Ascending Sort':
                    list_entries = ListModel.objects.order_by('due_date').filter(is_complete = False)
                    return render(request, "list/date_sort_view.html", {
                    "msg": "Ascending Sort",
                    "content": list_entries,
                    "sort_form": DateSelectForm()
                })
                case 'Descending Sort':
                    list_entries = ListModel.objects.order_by('-due_date').filter(is_complete = False)
                    return render(request, "list/date_sort_view.html", {
                    "msg": "Descending Sort",
                    "content": list_entries,
                    "sort_form": DateSelectForm()
                })
                case _:
                    type_ls = type.split(" ")
                    list_entries = ListModel.objects.filter(due_date = datetime.strptime(type_ls[2], "%Y-%m-%d").date(), is_complete = False)
                    return render(request, "list/date_sort_view.html", {
                        "msg": type,
                        "content": list_entries,
                        "sort_form": DateSelectForm()
                    })
        else:
            return render(request, "list/remove_view.html", {
                'form': form,
                'type': type
            })

@login_required(login_url='/')
def discard(request):
    if request.method == 'GET':
            # display relevant tasks for selection
            return render(request, "list/remove_view.html", {
                'form': RemoveSelectionForm(type = 'complete')
            })
    elif request.method == 'POST':
        form = RemoveSelectionForm(data=request.POST, type = 'complete')
        if form.is_valid():
            completed_tasks = form.cleaned_data['tasks']
            completed_tasks.delete()
            return redirect('complete')
        else:
            return render(request, "list/remove_view.html", {
            'form': form,
        })