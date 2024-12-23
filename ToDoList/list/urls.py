from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('content', views.list_view, name='list'),
    path('content/add', views.entry_add, name='add'),
    path('<int:entry_id>/edit', views.entry_edit, name='edit'),
    path('<int:entry_id>', views.entry, name = 'entry'),
    path('show/<int:priority>', views.priority_sort, name = 'priority'), # sorting by priority
    path('show/date', views.date_sort, name = 'date') # sorting by date
]   
