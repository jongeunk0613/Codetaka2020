import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer


from .models import Class, Comment

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
      className = data['className']
      userName = data['userName']
      
      user = User.objects.get(username=userName)
      newClass = Class.objects.create(user=user, name=className)
      
      # Send message to class group
      async_to_sync(self.channel_layer.group_send)(
         self.classGroupName,
         {
            'type': 'createClass',
            'className': className,
            'userName': userName,
            'timestamp': json.dumps(newClass.timestamp, cls=DjangoJSONEncoder)
         }
      )
      
   # Receive message from Class group
   def createClass(self, event):
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
      cId = data['cId']
      
      comment = Comment.objects.get(pk=cId)
      
      #Send message to room group
      async_to_sync(self.channel_layer.group_send)(
         self.sc_group_name, {
         'type': 'commentCreated',
         'cId': comment.idNumber,
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
      
   # Receive message from room group
   def commentCreated(self, event):
      
      # Send message to WebSocket
      self.send(text_data=json.dumps({
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
   
