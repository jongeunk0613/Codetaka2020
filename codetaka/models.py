from django.db import models
from django.contrib.auth.models import User

class Class(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   name = models.CharField(max_length=254)
   timestamp = models.DateTimeField()

class SourceCode(models.Model):
   name = models.CharField(max_length=200, blank=True)
   content = models.FileField(upload_to='sourceCodes/')
   upload_time = models.DateTimeField(auto_now_add=True)

   def __str__(self):
      return self.content.name

class Folder(models.Model):
   ofFolder = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
   ofClass = models.ForeignKey(Class, on_delete=models.CASCADE)
   name = models.CharField(max_length=254)
   timestamp = models.DateField(auto_now_add=True)
   
class Comment(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   scId = models.ForeignKey(SourceCode, on_delete=models.CASCADE)
   seltxt = models.TextField()
   anchorNodeID = models.CharField(max_length=255)
   anchorOffset = models.PositiveIntegerField(default = 0)
   focusNodeID = models.CharField(max_length=255)
   focusOffset = models.PositiveIntegerField(default = 0)
   posX = models.PositiveIntegerField(default = 0)
   posY = models.PositiveIntegerField(default = 0)
   text = models.TextField()
   timestamp = models.DateTimeField()
   lastEdited = models.DateTimeField()

   def __str__(self):
      return "[" + str(self.id) + "]: " + self.text


class Message(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   sc = models.ForeignKey(SourceCode, on_delete=models.CASCADE)
   ofClass = models.ForeignKey(Class, on_delete=models.CASCADE)
   content = models.TextField()
   timestamp = models.DateTimeField()
