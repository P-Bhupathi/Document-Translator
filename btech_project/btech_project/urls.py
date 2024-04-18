from django.conf.urls.static import static
from btech_project import settings 
from django.contrib import admin
from django.urls import path
from btech_app.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',login,name='login'),
    path('home',home,name='home'),
    path('time/',time,name='time'),
    path('insert_data/',insert_data,name='inset_data'),
    path('download/<str:path>/<str:name>/<str:language>/',download,name="download"),
    path('translate/<str:username>/<str:name>/<str:language>/',translate,name="translate"),
    path('delete/<str:name>/<str:lang>',delete,name='delete'),
    path('delete_original/<str:name>',delete_original, name='delete_original'),
    #path('login/',login,name="login"),
    path('signup/',signup,name="signup"),
    path('valid_login/',valid_login,name="valid_login"),
    path('valid_signup/',valid_signup,name="valid_signup"),
    path('logout/',logout,name='logout')
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
