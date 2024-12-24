from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from django.urls import reverse
from django import forms
from .models import ListModel

# Create your views here.

class NewEntryForm(forms.Form):
    title = forms.CharField(label="Title",max_length=32, required=True)
    description = forms.CharField(label="Description", required=True)
    priority = forms.IntegerField(label="Priority", min_value=1, max_value=3, required=True)
    due_date = forms.DateField(label="Due Date",required=True,  widget=forms.DateInput(attrs={'type': 'date'}))

def index(request):
    return render(request, "list/index.html")

def list_view(request):
    return render(request, "list/list_view.html", {
        "content": ListModel.objects.all()
    })

def entry_add(request):
    # render 'list' if no callback is provided
    callback = request.GET.get('callback', 'list')
    if request.method == "GET":
        # add a new entry
        return render(request, "list/entry_add.html", {
            "form": NewEntryForm(),
            "callback": callback
        })
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority')
        due_date = request.POST.get('due_date')
        if not title or not description or not priority or not due_date:
            return render(request, "list/entry_add.html", {
                "aux_message": "Any value can't be empty. Please try again."
            })
        ListModel.objects.create(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date
        )
        return redirect(reverse(callback))

    return HttpResponseBadRequest("Invalid request method.")


def entry_done(request):
    pass

def entry(request, entry_id):
    return render(request, "list/entry.html", {
        "entry": ListModel.objects.filter(id = entry_id).first()
    })
