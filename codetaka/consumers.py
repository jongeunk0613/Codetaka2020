import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer


from .models import Class, Comment, Message

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
         
         #Send message to room group
         async_to_sync(self.channel_layer.group_send)(
            self.sc_group_name, {
            'type': 'commentDeleted',
            'todoType': "commentDeleted",
            'cId': cId,
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
