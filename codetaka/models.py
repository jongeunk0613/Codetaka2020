from django.db import models
from django.contrib.auth.models import User

class Class(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   name = models.CharField(max_length=254)
   timestamp = models.DateField(auto_now_add=True)

class SourceCode(models.Model):
   name = models.CharField(max_length=200, blank=True)
   content = models.FileField(upload_to='sourceCodes/')
   upload_time = models.DateTimeField(auto_now_add=True)

   def __str__(self):
      return self.content.name


