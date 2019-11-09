# -*- coding: <utf-8> -*-
from django.db import models
import requests
import json
from django.contrib import messages
from Chatbot.models import *
from django.core.exceptions import ValidationError
from jinja2 import Template
from django.conf import settings

class Page(models.Model):
	page_fbid = models.CharField(max_length = 200,primary_key = True)
	page_token = models.CharField(max_length = 200)
	page_name = models.CharField(max_length = 150)
	page_location = models.CharField(max_length = 100,blank = True)
	page_fan_count = models.IntegerField()
	BOT_ENABLED = models.BooleanField(default = False)

	def __str__(self):
		return self.page_name

	def getfullName(self,userfbid):
		user_details_url = "https://graph.facebook.com/v2.6/{}".format(userfbid)
		user_details_params = {"fields":"first_name,last_name" ,"access_token":self.page_token}
		user_info = requests.get(user_details_url, user_details_params).json()
		full_name = user_info["first_name"] + " " + user_info["last_name"]
		return full_name
	def getfirstName(self,userfbid):
		user_details_url = "https://graph.facebook.com/v2.6/{}".format(userfbid)
		user_details_params = {"fields":"first_name,last_name" ,"access_token":self.page_token}
		user_info = requests.get(user_details_url, user_details_params).json()
		return user_info["first_name"]
	def getlastName(self,userfbid):
		user_details_url = "https://graph.facebook.com/v2.6/{}".format(userfbid)
		user_details_params = {"fields":"first_name,last_name" ,"access_token":self.page_token}
		user_info = requests.get(user_details_url, user_details_params).json()
		return user_info["last_name"]


	def Notify(self,post):
		if isinstance(post,TextPost) or isinstance(post,ImagePost):
			full_name = self.getfullName(post.creator_fbid)
			button = {"type":"postback","title":"Delete","payload":"delete:{}".format(str(post.id))}
			if isinstance(post,TextPost):
				notification_text = "From: {}\nTo: {}\nMessage:\n{}\n".format(full_name,self.page_name,post.post_text)
				if post.post_url != "":
					notification_text += "URL: {}".format(post.post_url)
				if post.post_fbid == "":
					button = None
					notification_text += "\n MESSAGE BLOCKED BY BOT"
			elif isinstance(post,ImagePost):
				notification_text = "From: {}\nTo: {}\nMessage:\n{}\nAttached image URL:{}".format(full_name,self.page_name,post.image_caption,post.image_url)
				if post.post_fbid == "":
					button = None
					notification_text += "\n MESSAGE BLOCKED BY BOT"
		else:
			full_name = self.getfullName(post)
			notification_text = "Notification from:{}\n {} wants to ask questions".format(self.page_name,full_name)
			inbox_url = self.getConversationURL(post)
			url = "https://www.facebook.com{}".format(inbox_url)
			button = {"type":"web_url","title":"Go to live chat","url":url}

		
		notifications = Notification.objects.all()
		for notification in notifications:
			post_message_url = "https://graph.facebook.com/v4.0/me/messages?access_token={}".format(notification.notifier.page_token)
			if button is not None:
				response_mssg = json.dumps({
            		        "recipient":{"id":int(notification.receiver)}, 
            	    	    "message":{"attachment":{
            	        	"type":"template",
            	           	"payload":{
            	            "template_type":"button",
            	            "text": notification_text, 
            	            "buttons":[
            	            	button,
         		               	]
        		                }
        		                }}
        		                })
			else:
				response_mssg = json.dumps({
					"messaging_type":"RESPONSE",
					"recipient":{"id":int(notification.receiver)},
					"message":{
					"text":notification_text
					}
					})

			status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_mssg)
			print(status.json())
		return True			



	def Subscribe(self,message):
		try:
			notification = Notification.objects.get(notifier= self)
			if notification.challenge == message['message']['text']:
				notification.receiver = message['sender']['id']
				notification.save()
				return True
			else:
				return False
		except:
			return False



	def Respond(self,response_mssg):
		fbid = json.loads(response_mssg)['recipient']['id']
		template = Template(response_mssg)
		response_mssg = template.render(page_name= self.page_name,
										page_location= self.page_location, 
										fan_count= self.page_fan_count, 
										full_name= self.getfullName(fbid),
										first_name= self.getfirstName(fbid),
										last_name= self.getlastName(fbid))
		post_message_url = "https://graph.facebook.com/v4.0/me/messages?access_token={}".format(self.page_token)
		status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_mssg.encode('utf-8'))
		return status.json()

	def getConversationURL(self,senderfbid):
		conv_id_url = "https://graph.facebook.com/v4.0/{}/conversations?access_token={}&fields=senders&user_id={}".format(self.page_fbid,self.page_token,senderfbid)
		conv_id_req = requests.get(conv_id_url, headers={"Content-Type": "application/json"})
		conv_id = conv_id_req.json()['data'][0]['id']
		conv_url = "https://graph.facebook.com/v5.0/{}?fields=link&access_token={}".format(conv_id,self.page_token)
		conv_req = requests.get(conv_url, headers={"Content-Type": "application/json"})
		return conv_req.json()['link']

	def getUserInput(self,senderfbid):
		conv_id_url = "https://graph.facebook.com/v4.0/{}/conversations?access_token={}&fields=senders&user_id={}".format(self.page_fbid,self.page_token,senderfbid)
		conv_id_req = requests.get(conv_id_url, headers={"Content-Type": "application/json"})
		conv_id = conv_id_req.json()['data'][0]['id']
		conv_url = "https://graph.facebook.com/v4.0/{}/messages?access_token={}&message=".format(conv_id,self.page_token)
		conv_req = requests.get(conv_url, headers={"Content-Type": "application/json"})
		last_mssg_id = conv_req.json()['data'][1]['id']
		message_url = "https://graph.facebook.com/v4.0/{}?access_token={}&fields=message,from".format(last_mssg_id,self.page_token)
		mssg_req = requests.get(message_url, headers={"Content-Type": "application/json"})
		message = mssg_req.json()
		message_text = message['message']
		message_from = message['from']['id']
		if message_from == self.page_fbid:
			try:
				input_ins = Input.objects.get(input_placeholder = message_text)
				return input_ins
			except Exception as e :
				return None
		else:
			return None



	def InitializeChatBOT(self):
		getStartedButton = Button.objects.get(button_label = "GET STARTED")
		get_started = "https://graph.facebook.com/v4.0/me/messenger_profile?access_token={}".format(self.page_token)
		subscribe = "https://graph.facebook.com/v4.0/{}/subscribed_apps?subscribed_fields=messages,messaging_postbacks&access_token={}".format(self.page_fbid,self.page_token)
		params = json.dumps({
						"get_started":{
							"payload": str(getStartedButton.id)
								}})
		try:
			status1 = requests.post(get_started, headers={"Content-Type": "application/json"},data=params)
			status2 = requests.post(subscribe, headers={"Content-Type": "application/json"})
			if (status1.json()['result'] == 'success' and status2.json()['success'] == True):
				self.BOT_ENABLED = True
				self.save()
				return True
		except Exception as e:
			return False
			messages.error("ERROR {} Retry please.".format(e))

	def whiteListFQDN(self):
		whitelist_domain_url = "https://graph.facebook.com/v4.0/me/messenger_profile?access_token={}".format(self.page_token)
		params = json.dumps({
  			"whitelisted_domains":[
    			"{}/payment".format(settings.FQDN)
  				]
		})
		status1 = requests.post(whitelist_domain_url, headers={"Content-Type": "application/json"},data=params)



class Notification(models.Model):
	notifier = models.ForeignKey(Page, on_delete= models.CASCADE)
	challenge = models.CharField(max_length= 45)
	receiver = models.CharField(max_length = 45,blank= True)

	def clean(self):
		count = Notification.objects.all().count()
		if count >= 1:
			raise ValidationError("Cannot add more than one row")

	def __str__(self):
		return str(self.notifier)