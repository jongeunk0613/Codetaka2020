from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from datetime import datetime
from django.forms.models import model_to_dict
from json import dumps
import json

from .forms import SignUpForm, SCUploadForm
from .models import Class, SourceCode, Comment, Message, Mention, Folder, ConnectedUser

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
      'sclist': SourceCode.objects.filter(ofClass=Class.objects.get(name=className)),
      'className': className,
      'folderlist': Folder.objects.all().filter(ofClass = Class.objects.get(name=className)),
   }
   if request.method == 'POST':
      form = SCUploadForm(request.POST, request.FILES)
      if form.is_valid():
         form.save()
         sc = SourceCode.objects.last()
         scname = sc.content.name.split('/')[-1]
         if scname.count("_") > 0:
            sctype = scname.split('.')[-1]
            scname = scname.split('_')[0:-1]
            scname = "_".join(scname)
            sc.name = scname + "." + sctype
         else:
            sc.name = scname
         
         ofClass = Class.objects.get(name=className)
         sc.ofClass = ofClass
         sc.save()
     #    return render(request, 'trying.html', {'text': 'success'})
     # else:
     #    return render(request, 'result.html', {'text': 'fail'})
         return redirect('openSC', className=className, sc_id=sc.id)
   form = SCUploadForm()
   sclist = SourceCode.objects.all()
   return render(request, 'mainpage.html', context)

# ADD FOLDER
def addFolder(request):
   if request.method == "GET":
      inClass = Class.objects.get(name = request.GET['classname'])
      newFolder = Folder(ofClass=inClass, name=request.GET['foldername'], timestamp=timezone.now())
      newFolder.save()
      return HttpResponse(newFolder.id)

   else:
      return HttpResponse('NOT A GET REQUEST')

# change to save source code, and divide the bottom part to open source code
# OPEN SOURCE CODE
@login_required
def openSC(request, className, sc_id):
   if request.method == 'POST':
      form = SCUploadForm(request.POST, request.FILES)
      if form.is_valid():
         form.save()
         sc = SourceCode.objects.last()
         scname = sc.content.name.split('/')[-1]
         if scname.count("_") > 0:
            sctype = scname.split('.')[-1]
            scname = scname.split('_')[0:-1]
            scname = "_".join(scname)
            sc.name = scname + "." + sctype
         else:
            sc.name = scname
         
         ofClass = Class.objects.get(name=className)
         sc.ofClass = ofClass
         sc.save()

   sc = get_object_or_404(SourceCode, pk=sc_id)
   sc.content.open(mode="r")
   sc_content = sc.content.read()
   sc.content.close()
   
   commentlist = serializers.serialize("json", Comment.objects.all().filter(scId=sc_id))
   if (len(Comment.objects.all()) > 0):
      nextID = Comment.objects.last().pk + 1
   else:
      nextID = -1
   
   #print(ConnectedUser.objects.all().filter(sc=sc))
      
   context = {
      'user': request.user,
      'form': SCUploadForm(),
      'sclist': SourceCode.objects.filter(ofClass=Class.objects.get(name=className)),
      'className': className,
      'sc': sc,
      'classUsername': Class.objects.get(name=className).user.username,
      'js_fcontent': dumps(sc_content),
      'range' : range(1, len(sc_content.split("\n"))+1),
      'nextId': nextID,
      'commentlist': commentlist,
      'messagelist': serializers.serialize("json", Message.objects.all().filter(sc=sc).order_by("-timestamp")),
      'mentionlist': serializers.serialize("json", Mention.objects.all().filter(scId=sc).order_by("-timestamp")),
      'folderlist': Folder.objects.all().filter(ofClass = Class.objects.get(name=className)),
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
      comment = Comment.objects.create(user = request.user, scId = scId, seltxt=request.GET['seltxt'],  anchorNodeID=request.GET['anchorNodeID'], anchorOffset=request.GET['anchorOffset'], focusNodeID=request.GET['focusNodeID'],focusOffset=request.GET['focusOffset'],posX=request.GET['posX'],posY=request.GET['posY'],text=request.GET['text'], timestamp = timezone.now(), lastEdited = timezone.now(), type = "Comment")
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
         data = str(comment.id) + " " + comment.anchorNodeID + " " + comment.focusNodeID
         comment.delete()
         return HttpResponse(data)
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
      message = Message.objects.create(user = user, sc = sc, ofClass = ofClass, content = request.GET['messageContent'], timestamp = timezone.now(), type="Message")
      message.save()
      return HttpResponse(message.id)
   return HttpResponse("NOT A GET")

# SAVE MENTION
@login_required
def saveMention(request):
   if request.method == "GET":
      scId = SourceCode.objects.only('id').get(id = request.GET['scId'])
      mention = Mention.objects.create(user = request.user, scId = scId, seltxt=request.GET['seltxt'],  anchorNodeID=request.GET['anchorNodeID'], anchorOffset=request.GET['anchorOffset'], focusNodeID=request.GET['focusNodeID'],focusOffset=request.GET['focusOffset'],text=request.GET['text'], timestamp = timezone.now(), type="Mention")
      mention.save()
      return HttpResponse(mention.id)
   else:
      return HttpResponse('error')

# GET COMMENT IDS
@login_required
def getCommentIDs(request):
   if request.method == "GET":
      sc = SourceCode.objects.get(pk = request.GET['scId'])
      commentlist = serializers.serialize("json", Comment.objects.all().filter(scId=sc))
      return HttpResponse(commentlist)
   else:
      return HttpResponse('error')

# SAVE CONNECTED USER
@login_required
def userConnected(request):
   if request.method == "GET":
      sc = SourceCode.objects.get(pk = request.GET['scId'])
      '''if ConnectedUser.objects.filter(sc = sc, user = request.user).exists() != True:
         cUser = ConnectedUser(user = request.user, userName = request.user.username, sc = sc, connectedTime = timezone.now(), disconnectedTime = timezone.now())
         cUser.save()
      else:
         cUser = ConnectedUser.objects.get(sc = sc, user = request.user)
         if (((timezone.now() - cUser.disconnectedTime).total_seconds() / 60) > 60 == True):
            print("PASSED")
            '''
      cUser = ConnectedUser(user = request.user, userName = request.user.username, sc = sc, connectedTime = timezone.now(), disconnectedTime = timezone.now())
      cUser.save()
      return HttpResponse('Done')
   else:
      return HttpResponse('error')
      
# SAVE DISCONNECTED USER
@login_required
def userDisconnected(request):
   if request.method == "GET":
      sc = SourceCode.objects.get(pk = request.GET['scId'])
      cUser = ConnectedUser.objects.filter(sc = sc, user = request.user)
      #cUser.disconnectedTime = timezone.now()
      cUser.delete()
      return HttpResponse('Done')
   else:
      return HttpResponse('error')

# GET CONNECTED USERS
@login_required
def getConnectedUsers(request):
   if request.method == "GET":
      sc = SourceCode.objects.get(pk = request.GET['scId'])
      connectedUsers = serializers.serialize("json", ConnectedUser.objects.all().filter(sc=sc))
      return HttpResponse(connectedUsers)
   else:
      return HttpResponse('error')

# GET SPEAKER USER
@login_required
def getSpeakerUser(request):
   if request.method == "GET":
      sc = SourceCode.objects.get(pk = request.GET['scId'])
      # change to sc = sc
      speakerUser = serializers.serialize("json", ConnectedUser.objects.filter(user = request.user).order_by("connectedTime"))
      return HttpResponse(speakerUser)
   else:
      return HttpResponse('error')


# TESTING
def trying(request):
   return render(request, "trying.html")

