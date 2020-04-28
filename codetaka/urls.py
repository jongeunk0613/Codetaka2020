from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signUp/', views.signUp, name='signUp'),
    path('signIn/', views.signIn, name='signIn'),
    path('signOut/', views.signOut, name='signOut'),
    path('classList/', views.classList, name='classList'),
    path('addClass/', views.addClass, name='addClass'),
    path('class/<str:className>/', views.openClass, name='openClass'),
    path('class/<str:className>/<int:sc_id>/', views.openSC, name='openSC'),
    path('saveComment/', views.saveComment, name='saveComment'),
    path('sendMessage/', views.sendMessage, name='sendMessage'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
