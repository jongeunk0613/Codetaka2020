from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
   re_path(r'ws/class/(?P<className>\w+)/$', consumers.ClassConsumer),
   re_path(r'ws/sourcecode/(?P<scId>\d+)/$', consumers.scConsumer),
   re_path(r'ws/folder/(?P<folderName>\w+)/$', consumers.FolderConsumer),
]
