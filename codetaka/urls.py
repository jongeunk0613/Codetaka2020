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
    path('addFolder/', views.addFolder, name='addFolder'),
    path('class/<str:className>/', views.openClass, name='openClass'),
    path('class/<str:className>/<int:sc_id>/', views.openSC, name='openSC'),
    path('getLatestCommentId/', views.getLatestCommentId, name='getLatestCommentId'),
    path('saveComment/', views.saveComment, name='saveComment'),
    path('deleteComment/', views.deleteComment, name='deleteComment'),
    path('saveEditedComment/', views.saveEditedComment, name='saveEditedComment'),
    path('sendMessage/', views.sendMessage, name='sendMessage'),
    
    path('trying/', views.trying, name='trying'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
