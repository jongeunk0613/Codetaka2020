from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('codetaka/', include('codetaka.urls')),
    path('admin/', admin.site.urls),
]
