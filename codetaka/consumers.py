import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer


from .models import Class

User = get_user_model()

class ClassConsumer(AsyncWebsocketConsumer):

   async def connect(self):
      self.className = self.scope['url_route']['kwargs']['className']
      self.classGroupName = 'class_%s' % self.className
      
      # Join class group
      await self.channel_layer.group_add(
         self.classGroupName,
         self.channel_name
      )
      
      await self.accept()
      
   async def disconnect(self, close_code):
      # Leave class group
      await self.channel_layer.group_discard(
         self.classGroupName,
         self.channel_name
      )
    
   # Receive message from WebSocket
   async def receive(self, text_data):
      data = json.loads(text_data)
      className = data['className']
      userName = data['userName']
      
      user = await database_sync_to_async(User.objects.get)(username=userName)
      newClass = await database_sync_to_async(Class.objects.create)(user=user, name=className)
      
      # Send message to class group
      await self.channel_layer.group_send(
         self.classGroupName,
         {
            'type': 'createClass',
            'className': className,
            'userName': userName,
            'timestamp': json.dumps(newClass.timestamp, cls=DjangoJSONEncoder)
         }
      )
      
   # Receive message from Class group
   async def createClass(self, event):
      className = event['className']
      userName = event['userName']
      timestamp = event['timestamp']
      
      # Send message to WebSocket
      await self.send(text_data = json.dumps({'className': className, 'userName': userName, 'timestamp': json.dumps(timestamp, cls=DjangoJSONEncoder)}))
