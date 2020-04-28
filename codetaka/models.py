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

class Comment(models.Model):
   scId = models.ForeignKey(SourceCode, on_delete=models.CASCADE)
   idNumber = models.PositiveIntegerField(default = 0)
   seltxt = models.CharField(max_length=255)
   anchorNodeID = models.CharField(max_length=255)
   anchorOffset = models.PositiveIntegerField(default = 0)
   focusNodeID = models.CharField(max_length=255)
   focusOffset = models.PositiveIntegerField(default = 0)
   posX = models.PositiveIntegerField(default = 0)
   posY = models.PositiveIntegerField(default = 0)
   text = models.CharField(max_length=255)

   def __str__(self):
      return "[" + str(self.id) + "]: " + self.text
