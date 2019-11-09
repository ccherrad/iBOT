from django.urls import path
from .views import * 

urlpatterns = [
	path('messages',SpottedBotView.as_view()),
	path('add-pages',addPagesView)
]