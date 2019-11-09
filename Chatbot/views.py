from django.http import HttpResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
import requests
import facebook
from django.utils import six
from django.conf import settings
from .models import * 
from Page.models import *
import random 


def Execute(page,sender_fbid,action):
    if action.action_type == "Reply":
         page.Respond(action.message.toJson(sender_fbid))
         if action.notification:
            page.Notify(sender_fbid)
    elif action.action_type == "Input":
        page.Respond(action.inputs.all()[0].toJson(sender_fbid))
    elif action.action_type == "Publish":
        post_ins = action.createPost(sender_fbid,page)
        if post_ins.filter():
            category = post_ins.categorize()
            if not action.advertise:
                post_fbid = post_ins.publish(category)
                page.Respond(action.message.toJson(sender_fbid))
                post_ins.post_fbid= post_fbid['id']
                post_ins.save()
                page.Notify(post_ins)
            else:
                page.Respond(action.message.advertise(sender_fbid))
        else:
            page.Respond(json.dumps({
                "messaging_type":"RESPONSE",
                "recipient": {"id":int(sender_fbid)} ,
                "message":{
                "text":"Ce Spotted ne sera pas publié car il n’est pas approprié!"
                }
                }))
            page.Notify(post_ins)
    



class SpottedBotView(View):
        def get(self, request, *args, **kwargs):
                if self.request.GET.get('hub.verify_token') == '123456789':
                        return HttpResponse(self.request.GET['hub.challenge'])
                else:
                        return HttpResponse('Error, invalid token')

        @method_decorator(csrf_exempt)
        def dispatch(self, request, *args, **kwargs):
                return View.dispatch(self, request, *args, **kwargs)

        def post(self, request, *args, **kwargs):
                try:
                        incoming_message = json.loads(self.request.body.decode('utf-8'))
                        print(incoming_message)
                        for entry in incoming_message['entry']:
                                for message in entry['messaging']:
                                        if 'message' in message and "attachments" in message['message'] :
                                            page_ins = Page.objects.get(page_fbid = message['recipient']['id'])
                                            input_ins = page_ins.getUserInput(message['sender']['id'])
                                            if input_ins is not None:  
                                                response_ins = Response.objects.create(input_ref = input_ins,value = message['message']['attachments'][0]["payload"]["url"] ,user_fbid = message['sender']['id'])
                                                action_ins = input_ins.input_action
                                                Execute(page_ins,message['sender']['id'],action_ins)

                                        elif 'message' in message:
                                            page_ins = Page.objects.get(page_fbid = message['recipient']['id'])
                                            input_ins = page_ins.getUserInput(message['sender']['id'])
                                            if input_ins is not None:
                                                print(input_ins.input_type)
                                                response_ins = Response.objects.create(input_ref = input_ins,value = message['message']['text'] ,user_fbid = message['sender']['id'])
                                                action_ins = input_ins.input_action
                                                Execute(page_ins,message['sender']['id'],action_ins)
                                            

                                            elif page_ins.Subscribe(message):
                                                page_ins.Respond(json.dumps({
                                                                    "messaging_type":"RESPONSE",
                                                                    "recipient": {"id":int(message['sender']['id'])} ,
                                                                    "message":{
                                                                    "text":"Please delete the challenge message (Y)"
                                                                            }
                                                                            }))
                                            elif message['message']['text'].startswith('/'):
                                                command_ins = Command.objects.get(command_text= message['message']['text'].replace('/','').lower())
                                                Execute(page_ins,message['sender']['id'],command_ins.command_action)
                                            else:
                                                page_ins.Respond(random.choice(Message.objects.filter(default= True)).toJson(message['sender']['id'])) 

                                        elif 'postback' in message :
                                            page_ins = Page.objects.get(page_fbid = message['recipient']['id'])
                                            try:
                                                button_ins = Button.objects.get(id = message['postback']['payload'])
                                                action_ins = button_ins.action
                                                Execute(page_ins,message['sender']['id'],action_ins)
                                            except Exception as e :
                                                lis = message['postback']['payload'].split(":")
                                                try:
                                                    post_ins = TextPost.objects.get(id = int(lis[1]))
                                                    post_ins.delete()
                                                except:
                                                    post_ins = ImagePost.objects.get(id = int(lis[1]))
                                                    post_ins.delete()

                except Exception as e:
                        print(e) 


                return HttpResponse()


def extendToken(access_token):
        graph = facebook.GraphAPI(access_token)
        app_id = settings.APP_ID
        app_secret = settings.APP_SECRET
        return graph.extend_access_token(app_id, app_secret)

def getPageToken(pagefbid,userToken):
        app_id = settings.APP_ID
        app_secret = settings.APP_SECRET
        url1 = "https://graph.facebook.com/v2.9/oauth/access_token?grant_type=fb_exchange_token&client_id={}&client_secret={}&fb_exchange_token={}".format(app_id,app_secret,userToken)
        status = requests.get(url1, headers={"Content-Type": "application/json"})
        token2 = status.json()['access_token']
        url2 = "https://graph.facebook.com/{}?fields=access_token&access_token={}".format(pagefbid,token2)
        status = requests.get(url2, headers={"Content-Type": "application/json"})
        return status.json()['access_token']

def getPages(userToken):
        graph = facebook.GraphAPI(userToken)
        return graph.get_object("/me/accounts")



@csrf_exempt
def addPagesView(request): 

        if request.POST:
                queryDict =  request.POST
                post_dict = dict(six.iterlists(request.POST))
                userToken = extendToken(post_dict['accessToken'][0])['access_token']
                pages_data = getPages(userToken)
                page_ids = []
                for page in pages_data['data']:
                        pageFbid = page['id']
                        page_ids.append(pageFbid)
                        try:
                                page_exist = Page.objects.get(page_fbid = pageFbid)
                        except:
                                neToken = getPageToken(pageFbid,userToken)
                                pageName = page['name']
                                url = "https://graph.facebook.com/v4.0/{}?fields=location,fan_count&access_token={}".format(pageFbid,neToken)
                                status = requests.get(url, headers={"Content-Type": "application/json"})
                                try:
                                        pageLocation = status.json()['location']['city']
                                except:
                                        pass
                                pageFancount = status.json()['fan_count']
                                page_ins = Page(page_fbid = pageFbid,
                                                                page_token = neToken, 
                                                                page_name = pageName, 
                                                                page_location = pageLocation , 
                                                                page_fan_count = pageFancount)
                                page_ins.save()

                for page in Page.objects.all():
                        if page.page_fbid not in page_ids:
                                page.delete()

        return HttpResponse("OK")
