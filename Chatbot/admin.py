from django.contrib import admin
from .models import * 
from .forms import MessageForm,ActionForm

admin.site.register(Button)
admin.site.register(Input)
admin.site.register(Command)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
	form = MessageForm

@admin.register(Action)
class MessageAdmin(admin.ModelAdmin):
	form = ActionForm
