from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from django.urls import reverse
from django import forms
from .models import ListModel
from .forms import EntryFormBuilder, EditSelectForm

# Create your views here.

def index(request):
    return render(request, "list/index.html")

def list_view(request):
    return render(request, "list/list_view.html", {
        "content": ListModel.objects.all(),
        "callback": "list"
    })

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
            due_date=due_date
        )
        if priority == 0:
            return redirect(reverse(callback))
        else:
            return redirect("priority", priority = priority)

    return HttpResponseBadRequest("Invalid request method.")


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


def entry(request, entry_id):
    return render(request, "list/entry.html", {
        "entry": ListModel.objects.filter(id = entry_id).first()
    })

def priority_sort(request, priority):
    if priority < 1 or priority > 3:
        return HttpResponseBadRequest("priority can only be between 1 (low) and 3 (high)")
    content = None
    if priority == 1:
        content = ListModel.objects.filter(priority = 1)
    elif priority == 2:
        content = ListModel.objects.filter(priority = 2)
    elif priority == 3:
        content = ListModel.objects.filter(priority = 3)
    return render(request, "list/list_view.html", {
        "content": content,
        "callback": "priority",
        "priority": priority
    })
