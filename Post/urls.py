from django.urls import path
from .views import *

urlpatterns = [
    path('', payment, name='payment'),
    path('schedule',schedule,name='schedule'), 
    path('invoice/<int:post_id>',invoice,name='invoice'), 
    path('success/<int:post_id>',success,name='success'),
    path('failed',failed,name='failed'),
    path('test',test,name='test'),
]