from django.db import models

# Create your models here.

class ListModel(models.Model):
    title = models.CharField(max_length=32)
    description = models.TextField()
    priority = models.IntegerField()
    due_date = models.DateField()

    def __str__(self):
        return self.title
