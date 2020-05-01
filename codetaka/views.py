from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from json import dumps
import json

from .forms import SignUpForm, SCUploadForm
from .models import Class, SourceCode, Comment, Message

# DEFAULT PAGE
def index(request):
   if request.user.is_authenticated:
      return redirect('classList')
   else:
      return redirect('signIn')

# SIGN UP
def signUp(request):
   if request.method == 'POST':
      form = SignUpForm(request.POST)
      if form.is_valid():
         form.save()
         return redirect('signIn')
   else:
      form = SignUpForm()
   return render(request, 'signup.html', {'form': form})

# SIGN IN
def signIn(request):
   context = {
      'text': "THIS IS CODE",
   }
   if request.method == 'POST':
      form = AuthenticationForm(data = request.POST)
      if form.is_valid():
         user = form.get_user()
         login(request, user)
         return redirect('index')
      else:
         form = AuthenticationForm()
         return render(request, 'signin.html', {'form': form, 'error': "Sign in failed."})
   form = AuthenticationForm()
   return render(request, 'signin.html', {'form': form})

# SIGN OUT
def signOut(request):
   logout(request)
   form = AuthenticationForm()
   return redirect('signIn')

# SHOW LIST OF CLASS
@login_required
def classList(request):
   context = {
      'classList': Class.objects.all()
   }
   return render(request, 'classes.html', context)
   
# CREATE CLASS
@login_required
def addClass(request):
   if request.method == "GET":
      newClass = Class(user=request.user, name=request.GET['classname'], timestamp=timezone.now())
      newClass.save()
      return HttpResponse(newClass.id)
   else:
      return HttpResponse('NOT A GET REQUEST')
   
# OPEN CLASS
@login_required
def openClass(request, className):
   context = {
      'user': request.user,
      'form': SCUploadForm(),
      'sclist': SourceCode.objects.all(),
      'className': className,
   }
   if request.method == 'POST':
      form = SCUploadForm(request.POST, request.FILES)
      if form.is_valid():
         form.save()
         return render(request, 'result.html', {'text': 'success'})
      else:
         return render(request, 'result.html', {'text': 'fail'})
   form = SCUploadForm()
   sclist = SourceCode.objects.all()
   return render(request, 'mainpage.html', context)

# OPEN SOURCE CODE
@login_required
def openSC(request, className, sc_id):
   sc = get_object_or_404(SourceCode, pk=sc_id)
   sc.content.open(mode="r")
   sc_content = sc.content.read()
   sc.content.close()
   
   commentlist = serializers.serialize("json", Comment.objects.all().filter(scId=sc_id))
   if (len(Comment.objects.all()) > 0):
      nextID = Comment.objects.last().pk + 1
   else:
      nextID = -1
   
   messagelist = serializers.serialize("json", Message.objects.all().filter(sc=sc))
   
   context = {
      'user': request.user,
      'form': SCUploadForm(),
      'sclist': SourceCode.objects.all(),
      'className': className,
      'sc': sc,
      'js_fcontent': dumps(sc_content),
      'range' : range(1, len(sc_content.split("\n"))+1),
      'nextId': nextID,
      'commentlist': commentlist,
      'messagelist': messagelist,
   }
   return render(request, 'mainpage.html', context)

# GET LATEST COMMENT ID
@login_required
def getLatestCommentId(request):
   if request.method == "GET":
      if (len(Comment.objects.all()) == 0):
         return HttpResponse(1)
      else:
         latest = Comment.objects.last()
         return HttpResponse(latest.pk + 1)

# CREATE COMMENT
@login_required
def saveComment(request):
   if request.method == "GET":
      scId = SourceCode.objects.only('id').get(id = request.GET['scId'])
      comment = Comment.objects.create(user = request.user, scId = scId, seltxt=request.GET['seltxt'],  anchorNodeID=request.GET['anchorNodeID'], anchorOffset=request.GET['anchorOffset'], focusNodeID=request.GET['focusNodeID'],focusOffset=request.GET['focusOffset'],posX=request.GET['posX'],posY=request.GET['posY'],text=request.GET['text'], timestamp = timezone.now(), lastEdited = timezone.now())
      comment.save()
      return HttpResponse(comment.id)
   else:
      return HttpResponse('error')

# DELETE COMMENT
@login_required
def deleteComment(request):
   if request.method == "GET":
      comment = Comment.objects.get(pk = request.GET['cId'])
      if request.user == comment.user:
         comment.delete()
         return HttpResponse("DELETED")
      else:
         return HttpResponse("NO ACCESS")
   else:
      return HttpResponse("NOT A GET REQUEST")
      
# SAVE EDITED COMMENT
@login_required
def saveEditedComment(request):
   if request.method == "GET":
      comment = Comment.objects.get(pk = request.GET['cId'])
      comment.text = request.GET['text']
      comment.lastEdited = timezone.now()
      comment.save()
      return HttpResponse(comment.id)
   else:
      return HttpResponse('error')

# CREATE MESSAGE
@login_required
def sendMessage(request):
   if request.method == "GET":
      sc = SourceCode.objects.only('id').get(id = request.GET['scId'])
      user = request.user
      ofClass = Class.objects.get(name=request.GET['classname'])
      message = Message.objects.create(user = user, sc = sc, ofClass = ofClass, content = request.GET['messageContent'], timestamp = timezone.now())
      message.save()
      return HttpResponse(message.id)
   return HttpResponse("NOT A GET")
