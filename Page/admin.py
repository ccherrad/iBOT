from django.contrib import admin
from .models import *
from django.conf import settings
import os 

admin.site.register(Notification)

def setup_bot(modeladmin, request, queryset):
	for page in queryset:
		page.InitializeChatBOT()
		page.whiteListFQDN()
		 
setup_bot.short_description = "Install Chatbot"



@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
	list_display = ['page_name','page_fan_count','BOT_ENABLED']
	change_list_template = os.path.join(settings.BASE_DIR, 'templates/admin/bot/page/change_list.html')
	actions = [setup_bot]

	def get_actions(self, request):
		actions = super().get_actions(request)
		if 'delete_selected' in actions:
			del actions['delete_selected']
		
		return actions

	def has_add_permission(self,request,obj=None):
		return False