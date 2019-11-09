from django.contrib import admin
from .models import * 
from .forms import ImagePostForm

def publish(modeladmin, request, queryset):
	for post in queryset:
		post_fbid = post.publish()
		print(post_fbid)

publish.short_description = "Publish post"


admin.site.register(ReachTime)
admin.site.register(Time)
admin.site.register(Filter)
admin.site.register(Word)
admin.site.register(Category)

@admin.register(TextPost)
class PostAdmin(admin.ModelAdmin):
	actions = [publish]

@admin.register(ImagePost)
class PostAdmin(admin.ModelAdmin):
	form = ImagePostForm
	
	actions = [publish]