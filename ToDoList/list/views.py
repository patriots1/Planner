from django.shortcuts import render
from django.http import HttpResponseBadRequest
from .models import ListModel

# Create your views here.

def list_view(request):
    return render(request, "list/list_view.html", {
        "content": ListModel.objects.all()
    })


def entry(request, entry_id):
    return render(request, "list/entry.html", {
        "entry": ListModel.objects.filter(id = entry_id).first()
    })
