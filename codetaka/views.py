from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from json import dumps
import json

from .forms import SignUpForm, SCUploadForm
from .models import Class, SourceCode, Comment

# DEFAULT PAGE
def index(request):
   if request.user.is_authenticated:
      return redirect('classList')
   else:
      return redirect('signIn')

def signUp(request):
   if request.method == 'POST':
      form = SignUpForm(request.POST)
      if form.is_valid():
         form.save()
         return redirect('signIn')
   else:
      form = SignUpForm()
   return render(request, 'signup.html', {'form': form})

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

def signOut(request):
   logout(request)
   form = AuthenticationForm()
   return redirect('signIn')

# SHOW LIST OF CLASS
def classList(request):
   context = {
      'classList': Class.objects.all().filter(user = request.user)
   }
   return render(request, 'classes.html', context)
   
def addClass(request):
   if request.method == "GET":
      newClass = Class(user=request.user, name=request.GET['className'])
      newClass.save()
      data = {
         'name': newClass.name,
         'user': newClass.user.username,
         'created': newClass.timestamp,
      }
      return JsonResponse({"info": data}, status=200)
   else:
      return HttpResponse('NOT A GET REQUEST')
      
def openClass(request, className):
   context = {
      'user': request.user.username,
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
   
def openSC(request, className, sc_id):
   sc = get_object_or_404(SourceCode, pk=sc_id)
   sc.content.open(mode="r")
   sc_content = sc.content.read()
   sc.content.close()
   
   commentlist = serializers.serialize("json", Comment.objects.all().filter(scId=sc_id))
   if (len(Comment.objects.all()) > 0):
      nextID = Comment.objects.last().idNumber
   else:
      nextID = -1;
   
   context = {
      'user': request.user.username,
      'form': SCUploadForm(),
      'sclist': SourceCode.objects.all(),
      'className': className,
      'sc': sc,
      'js_fcontent': dumps(sc_content),
      'range' : range(1, len(sc_content.split("\n"))+1),
      'nextId': nextID,
      'commentlist': commentlist,
   }
   return render(request, 'mainpage.html', context)

def saveComment(request):
   if request.method == "GET":
      scId = SourceCode.objects.only('id').get(id = request.GET['scId'])
      comment = Comment.objects.create(scId = scId, seltxt=request.GET['seltxt'], idNumber = request.GET['id'],  anchorNodeID=request.GET['anchorNodeID'], anchorOffset=request.GET['anchorOffset'], focusNodeID=request.GET['focusNodeID'],focusOffset=request.GET['focusOffset'],posX=request.GET['posX'],posY=request.GET['posY'],text=request.GET['text'])
      comment.save()
      if (Comment.objects.filter(scId = scId).exists() == True):
         return HttpResponse(comment.id)
      else:
         return HttpResponse('not exists')
   else:
      return HttpResponse('error')

def sendMessage(request):
   return HttpResponse("hi")
