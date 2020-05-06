import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer


from .models import Class, Comment, Message, Mention, Folder

User = get_user_model()

class ClassConsumer(WebsocketConsumer):

   def connect(self):
      self.className = self.scope['url_route']['kwargs']['className']
      self.classGroupName = 'class_%s' % self.className
      
      # Join class group
      async_to_sync(self.channel_layer.group_add)(
         self.classGroupName,
         self.channel_name
      )
      
      self.accept()
      
   def disconnect(self, close_code):
      # Leave class group
      async_to_sync(self.channel_layer.group_discard)(
         self.classGroupName,
         self.channel_name
      )
    
   # Receive message from WebSocket
   def receive(self, text_data):
      data = json.loads(text_data)
      classId = data['classId']
      
      newClass = Class.objects.get(pk=classId)
      
      # Send message to class group
      async_to_sync(self.channel_layer.group_send)(
         self.classGroupName,
         {
            'type': 'classCreated',
            'className': newClass.name,
            'userName': newClass.user.username,
            'timestamp': json.dumps(newClass.timestamp, cls=DjangoJSONEncoder)
         }
      )
      
   # Receive message from Class group
   def classCreated(self, event):
      className = event['className']
      userName = event['userName']
      timestamp = event['timestamp']
      
      # Send message to WebSocket
      self.send(text_data = json.dumps({'className': className, 'userName': userName, 'timestamp': json.dumps(timestamp, cls=DjangoJSONEncoder)}))

class scConsumer(WebsocketConsumer):
   def connect(self):
      self.sc_name = self.scope['url_route']['kwargs']['scId']
      self.sc_group_name = 'sourcecode_%s' % self.sc_name
      
      # Join room group
      async_to_sync(self.channel_layer.group_add)(
         self.sc_group_name,
         self.channel_name
      )
   
      self.accept()
      
   def disconnect(self, close_code):
      # Leave room group
      async_to_sync(self.channel_layer.group_discard)(
         self.sc_group_name,
         self.channel_name
      )
      
   # Receive message from WebSocket
   def receive(self, text_data):
      data = json.loads(text_data)
      todoType = data['todoType']
      
      if (todoType == "commentCreated") is True:
         cId = data['cId']
         
         comment = Comment.objects.get(pk=cId)
         
         #Send message to room group
         async_to_sync(self.channel_layer.group_send)(
            self.sc_group_name, {
            'type': 'commentCreated',
            'todoType': "commentCreated",
            'cId': comment.pk,
            'seltxt': comment.seltxt,
            'anchorNodeID': comment.anchorNodeID,
            'anchorOffset': comment.anchorOffset,
            'focusNodeID': comment.focusNodeID,
            'focusOffset': comment.focusOffset,
            'posx': comment.posX,
            'posy': comment.posY,
            'text': comment.text,
            }
         )
      elif (todoType == "commentEdited") is True:
         cId = data['cId']
         
         comment = Comment.objects.get(pk=cId)
         
         #Send message to room group
         async_to_sync(self.channel_layer.group_send)(
            self.sc_group_name, {
            'type': 'commentEdited',
            'todoType': "commentEdited",
            'cId': comment.pk,
            'seltxt': comment.seltxt,
            'anchorNodeID': comment.anchorNodeID,
            'anchorOffset': comment.anchorOffset,
            'focusNodeID': comment.focusNodeID,
            'focusOffset': comment.focusOffset,
            'posx': comment.posX,
            'posy': comment.posY,
            'text': comment.text,
            }
         )
      
      elif (todoType == "commentDeleted") is True:
         cId = data['cId']
         anchorNodeID = data['anchorNodeID']
         focusNodeID = data['focusNodeID']
         
         #Send message to room group
         async_to_sync(self.channel_layer.group_send)(
            self.sc_group_name, {
            'type': 'commentDeleted',
            'todoType': "commentDeleted",
            'cId': cId,
            'anchorNodeID': anchorNodeID,
            'focusNodeID': focusNodeID,
            }
         )
      elif (todoType == "messageSent") is True:
         messageId = data['messageId']
         
         message = Message.objects.get(pk=messageId)
         
         # Send message to room group
         async_to_sync(self.channel_layer.group_send)(
            self.sc_group_name, {
            'type': 'messageSent',
            'todoType': "messageSent",
            'userid': message.user.id,
            'scId': message.sc.id,
            'ofClass': message.ofClass.id,
            'content': message.content,
            'timestamp': json.dumps(message.timestamp, cls=DjangoJSONEncoder),
            }
         )
      elif (todoType == "autofocus") is True:
         scrollPos = data['scrollPos']
         
         async_to_sync(self.channel_layer.group_send)(
            self.sc_group_name, {
            'type': 'autofocus',
            'todoType': "autofocus",
            'scrollPos': scrollPos,
            }
         )
      elif (todoType == "speakerRequest") is True:
         fromU = data['fromU']
         toU = data['toU']
         
         async_to_sync(self.channel_layer.group_send)(
            self.sc_group_name, {
            'type': 'speakerRequest',
            'todoType': "speakerRequest",
            'fromU': fromU,
            'toU': toU,
            }
         )
      elif (todoType == "speakerRequestResponse") is True:
         ownerU = data['ownerU']
         requestU = data['requestU']
         response = data['response']
         
         async_to_sync(self.channel_layer.group_send)(
            self.sc_group_name, {
            'type': 'speakerRequestResponse',
            'todoType': "speakerRequestResponse",
            'ownerU': ownerU,
            'requestU': requestU,
            'response': response,
            }
         )
      elif (todoType == "autofocusSelection") is True:
         anchorNodeID = data['anchorNodeID']
         focusNodeID = data['focusNodeID']
         
         async_to_sync(self.channel_layer.group_send)(
            self.sc_group_name, {
            'type': 'autofocusSelection',
            'todoType': "autofocusSelection",
            'anchorNodeID': anchorNodeID,
            'focusNodeID': focusNodeID,
            }
         )
      elif (todoType == "mentionCreated") is True:
         mId = data['mId']
         
         mention = Mention.objects.get(pk=mId)
         
         #Send message to room group
         async_to_sync(self.channel_layer.group_send)(
            self.sc_group_name, {
            'type': 'mentionCreated',
            'todoType': "mentionCreated",
            'userid': mention.user.id,
            'username': mention.user.username,
            'mId': mention.pk,
            'seltxt': mention.seltxt,
            'anchorNodeID': mention.anchorNodeID,
            'anchorOffset': mention.anchorOffset,
            'focusNodeID': mention.focusNodeID,
            'focusOffset': mention.focusOffset,
            'text': mention.text,
            'timestamp': json.dumps(mention.timestamp, cls=DjangoJSONEncoder),
            }
         )
      
   # Receive message from room group
   def commentCreated(self, event):
      
      # Send message to WebSocket
      self.send(text_data=json.dumps({
         'todoType': "commentCreated",
         'cId': event['cId'],
         'seltxt': event['seltxt'],
         'anchorNodeID': event['anchorNodeID'],
         'anchorOffset': event['anchorOffset'],
         'focusNodeID': event['focusNodeID'],
         'focusOffset': event['focusOffset'],
         'posx': event['posx'],
         'posy': event['posy'],
         'text': event['text'],
                                     }))
   # Receive message from room group
   def commentEdited(self, event):
   
   # Send message to WebSocket
      self.send(text_data=json.dumps({
         'todoType': "commentEdited",
         'cId': event['cId'],
         'seltxt': event['seltxt'],
         'anchorNodeID': event['anchorNodeID'],
         'anchorOffset': event['anchorOffset'],
         'focusNodeID': event['focusNodeID'],
         'focusOffset': event['focusOffset'],
         'posx': event['posx'],
         'posy': event['posy'],
         'text': event['text'],
                                     }))
   
   # Receive message from room group
   def commentDeleted(self, event):
      
      # Send message to WebSocket
      self.send(text_data=json.dumps({
         'todoType': "commentDeleted",
         'cId': event['cId'],
         'anchorNodeID': event['anchorNodeID'],
         'focusNodeID': event['focusNodeID'],
                                     }))
                                     
   # Receive message from room group
   def messageSent(self, event):
      
      # Send message to WebSocket
      self.send(text_data=json.dumps({
         'todoType': "messageSent",
         'userid': event['userid'],
         'scId': event['scId'],
         'ofClass': event['ofClass'],
         'content': event['content'],
         'timestamp': json.dumps(event['timestamp'], cls=DjangoJSONEncoder),
                                     }))
                                     
    # Receive message from room group
   def autofocus(self, event):
    
       # Send message to WebSocket
       self.send(text_data=json.dumps({
          'todoType': "autofocus",
          'scrollPos': event['scrollPos'],
                                      }))
                                      
   # Receive message from room group
   def speakerRequest(self, event):
      
      # Send message to WebSocket
      self.send(text_data=json.dumps({
         'todoType': "speakerRequest",
         'fromU': event['fromU'],
         'toU': event['toU'],
                                     }))
                                     
   # Receive message from room group
   def speakerRequestResponse(self, event):
      
      # Send message to WebSocket
      self.send(text_data=json.dumps({
         'todoType': "speakerRequestResponse",
         'ownerU': event['ownerU'],
         'requestU': event['requestU'],
         'response': event['response'],
                                     }))
                                     
   # Receive message from room group
   def autofocusSelection(self, event):
      
      # Send message to WebSocket
      self.send(text_data=json.dumps({
         'todoType': "autofocusSelection",
         'anchorNodeID': event['anchorNodeID'],
         'focusNodeID': event['focusNodeID'],
                                     }))
                                     
   # Receive message from room group
   def mentionCreated(self, event):
      
      # Send message to WebSocket
      self.send(text_data=json.dumps({
         'todoType': "mentionCreated",
         'userid': event['userid'],
         'username': event['username'],
         'mId': event['mId'],
         'seltxt': event['seltxt'],
         'anchorNodeID': event['anchorNodeID'],
         'anchorOffset': event['anchorOffset'],
         'focusNodeID': event['focusNodeID'],
         'focusOffset': event['focusOffset'],
         'text': event['text'],
         'timestamp': json.dumps(event['timestamp'], cls=DjangoJSONEncoder),
                                     }))

class FolderConsumer(WebsocketConsumer):
   def connect(self):
      self.folderName = self.scope['url_route']['kwargs']['folderName']
      self.folderGroupName = 'folder_%s' % self.folderName

      async_to_sync(self.channel_layer.group_add)(
         self.folderGroupName,
         self.channel_name
      )

      self.accept()

   def disconnect(self, close_code):
      async_to_sync(self.channel_layer.group_discard)(
         self.folderGroupName,
         self.channel_name
      )

   def receive(self, text_data):
      data = json.loads(text_data)
      classId = data['classId']
      folderId = data['folderId']

      newFolder = Folder.objects.get(pk=folderId)

      async_to_sync(self.channel_layer.group_send)(
         self.folderGroupName,
         {
            'type': 'folderCreated',
            'ofClassName': newFolder.ofClass.name,
            'folderName': newFolder.name,
            'timestamp': json.dumps(newFolder.timestamp, cls=DjangoJSONEncoder)
         }
      )

   def folderCreated(self, event):
      ofClassName = event['ofClassName']
      folderName = event['folderName']
      timestamp = event['timestamp']

      self.send(text_data = json.dumps({'ofClassName': ofClassName, 'folderName': folderName, 'timestamp': json.dumps(timestamp, cls=DjangoJSONEncoder)}))

