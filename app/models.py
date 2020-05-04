from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# override User model to display email instead of username
def get_email(self):
    return self.email
User.add_to_class('__str__', get_email)

class List(models.Model):
    name = models.CharField(max_length=256)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    guest = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='lists', blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=24)
    quantity = models.CharField(max_length=12)
    parent_list = models.ForeignKey(List, on_delete=models.CASCADE)
    found = models.BooleanField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}: {1}'.format(self.parent_list, self.name)
