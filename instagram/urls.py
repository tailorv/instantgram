from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns=[
    path('',views.index, name = 'index'),
    path('profile/<str:username>/',views.profile,name='profile'),
    path('edit/profile/',views.update_profile,name='update'),
    path('image/',views.post,name='post'),
    path('search/', views.search_profile, name='search'),
    path('user_profile/<username>/', views.user_profile, name='user_profile'),
    path('unfollow/<to_unfollow>', views.unfollow, name='unfollow'),
    path('follow/<to_follow>', views.follow, name='follow'),
    path('image/<id>', views.comment, name='comment'),
    path('signup/', views.usersignup, name='signup'),
    path('activate/<uidb64>/<token>/',views.activate_account, name='activate'),

]
if settings.DEBUG:
    urlpatterns+= static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)