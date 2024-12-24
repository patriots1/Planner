from django.contrib.auth.models import User
from django.db import models

class UserModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hintModel')
    hint = models.CharField(max_length=64)

    def __str__(self):
        return self.hint