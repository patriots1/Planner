from django.shortcuts import render
from .models import ListModel

# Create your views here.

def list_view(request):
    return render(request, "list/list_view.html", {
        "content": ListModel.objects.all()
    })


def entry(request, entry_id):
    pass
