from django.db import models
import uuid
from django.core.exceptions import ValidationError
import json
from Post.models import *
from django.conf import settings

class Button(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	button_label = models.CharField(max_length = 45)
	button_text = models.CharField(max_length = 45)
	action = models.ForeignKey('Action', blank= True,null= True ,on_delete = models.SET_NULL)

	def __str__(self):
		return "{} ({})".format(self.button_text,self.button_label)

class Message(models.Model):
	message_label = models.CharField(max_length = 45)
	message_text = models.TextField()
	default = models.BooleanField(default= False)
	payment_succeeded = models.BooleanField(default= False)
	buttons = models.ManyToManyField(Button, blank= True)

	def __str__(self):
		return self.message_label

	def advertise(self,senderfbid):
		return json.dumps({
			"recipient":{"id":int(senderfbid)}, 
			"message":{
			"attachment":{
			"type":"template",
			"payload":{
			"template_type":"button",
			"text":self.message_text,
			"buttons":[
				{
				"type":"web_url",
				"url":"{}/payment/".format(settings.FQDN),
				"title":"Payer ici",
				"webview_height_ratio": "full",
				"messenger_extensions": True
				}
			]
			}
			}
			}
			})


	def toJson(self,senderfbid):

		if self.buttons.count() == 0 :
			return json.dumps({
				"messaging_type":"RESPONSE",
				"recipient": {"id":int(senderfbid)} ,
				"message":{
				"text":self.message_text
				}
				})
		else:
			jsonbuttons = [{"type":"postback","title":b.button_text,"payload":str(b.id)} for b in self.buttons.all() ]
			return json.dumps({
                        "recipient":{"id":int(senderfbid)}, 
                        "message":{"attachment":{
                        "type":"template",
                        "payload":{
                        "template_type":"button",
                        "text": self.message_text, 
                        "buttons":jsonbuttons
                        }
                        }}
                        })



class Input(models.Model):
	input_label = models.CharField(max_length= 45)
	input_placeholder = models.TextField()
	input_action = models.ForeignKey('Action',blank= True,null= True,on_delete = models.SET_NULL) 
	TEXT = "Text"
	IMAGE = "Image"
	URL = "URL"
	TYPE_CHOICES = (
			(TEXT, 'Text'),
			(IMAGE, 'Image'),
			(URL, 'URL')
		)
	input_type = models.CharField(max_length = 45, choices = TYPE_CHOICES)

	def toJson(self,senderfbid):
		return json.dumps({
                        "messaging_type":"RESPONSE", 
                        "recipient":{"id":senderfbid}, 
                        "message":{"text":self.input_placeholder}
                        })

	def __str__(self):
		return self.input_label

class Response(models.Model):
	input_ref = models.ForeignKey(Input, on_delete = models.CASCADE)
	value = models.TextField()
	user_fbid = models.CharField(max_length = 45)

	def __str__(self):
		return self.value

class Action(models.Model):
	action_label = models.CharField(max_length= 45)
	REPLY_MESSAGE = 'Reply'
	GET_INPUT = 'Input'
	PAGE_PUBLISH = "Publish"
	TYPE_CHOICES = (
		(REPLY_MESSAGE ,'Reply'),
		(GET_INPUT , 'Input'), 
		(PAGE_PUBLISH , 'Publish')
		)
	action_type = models.CharField(max_length= 45 , choices= TYPE_CHOICES, blank= False)
	message = models.ForeignKey(Message , on_delete = models.SET_NULL, blank = True, null= True )
	inputs = models.ManyToManyField(Input, blank= True)
	notification = models.BooleanField(default = False)
	advertise = models.BooleanField(default = False)

	def createPost(self,senderfbid,page):
		text = None 
		url = None 
		image_url = None 
		if self.action_type == "Publish":
			for inp in self.inputs.all():
				if inp.input_type == "Text":
					text_qs = Response.objects.filter(input_ref= inp,user_fbid= senderfbid).last()
					text = text_qs.value
					text_qs.delete()
				if inp.input_type == "URL":
					url_qs = Response.objects.filter(input_ref= inp,user_fbid= senderfbid).last()
					url = url_qs.value
					url_qs.delete()
				if inp.input_type == "Image":
					image_url_qs = Response.objects.filter(input_ref= inp,user_fbid= senderfbid).last()
					image_url = image_url_qs.value
					image_url_qs.delete()

		if text is not None and image_url is None:
			text_post_ins = TextPost()
			fullname = page.getfullName(senderfbid)
			text_post_ins.post_label = 'post from {}'.format(fullname)
			text_post_ins.creator_fbid = senderfbid
			text_post_ins.post_text = text 
			if url is not None:
				text_post_ins.post_url = url 
			text_post_ins.save()
			text_post_ins.publish_to.set([page])
			return text_post_ins
		elif image_url is not None and url is None:
			image_post_ins = ImagePost()
			fullname = page.getfullName(senderfbid)
			image_post_ins.post_label = 'post from {}'.format(fullname)
			image_post_ins.creator_fbid = senderfbid
			image_post_ins.image_url = image_url
			if text is not None:
				image_post_ins.image_caption = text
			image_post_ins.save()
			image_post_ins.publish_to.set([page])
			return image_post_ins

	def __str__(self):
		return self.action_label


class Command(models.Model):
	command_text = models.CharField(max_length= 45)
	command_action = models.ForeignKey(Action,null=True,on_delete=models.SET_NULL)

	
	def save(self, *args, **kwargs):
		self.command_text = self.command_text.lower()
		return super(Command, self).save(*args, **kwargs)


	def __str__(self):
		return self.command_text