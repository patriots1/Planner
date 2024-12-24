from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_view, name='list'), 
    path('<int:entry_id>', views.entry, name = 'entry')
]
