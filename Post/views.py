from django.shortcuts import render,redirect
from .forms import *
from django.views.decorators.http import require_POST
from datetime import datetime,timedelta
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import json
from Chatbot.models import * 
from django.conf import settings
import random

def payment(request):
	paymentForm = PaymentForm()
	reachTimeForm = ReachTimeForm()
	ctxt = {'paymentForm': paymentForm,'reachTimeForm':reachTimeForm}
	return render(request,"payment.html",context=ctxt)

@require_POST
def schedule(request):
	psid = request.POST.getlist('psid')[0]	
	reach_time = request.POST.getlist('reach_time')[0]
	nop = int(request.POST.getlist('nop')[0])
	post = Post.objects.filter(creator_fbid= psid).last()
	time = ReachTime.objects.get(id= reach_time)
	scheduling_days = getDates(time,nop)
	post.publish_at.clear()
	for sd in scheduling_days:
		post.publish_at.create(time=sd)
	return redirect("invoice/{}".format(post.id))

def invoice(request,post_id):
	post_ins = Post.objects.get(id= int(post_id))
	quantity = post_ins.publish_at.all().count()
	price = 5
	amount = quantity * 5 
	paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": price,
        "quantity":quantity,
        "payer":post_ins.creator_fbid,
        "item_name": "Advertisement {}".format(post_id),
        "invoice":str(post_id),
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return": request.build_absolute_uri(reverse('success',args=[post_id])),
        "cancel_return": request.build_absolute_uri(reverse('failed')),
    }
	try:
		text_post = TextPost.objects.get(id= post_ins.id)
		post_ins = text_post
	except:
		image_post = ImagePost.objects.get(id=post_ins.id)
		post_ins = image_post
	dates = []
	for date in post_ins.publish_at.all():
		dates.append(date.time.strftime("%b %d %Y %H:%M"))
	form = PayPalPaymentsForm(initial=paypal_dict)
	ctx = {"form": form,"post":post_ins,"amount":amount,"dates":dates}
	return render(request, "process.html",context= ctx)

def success(request,post_id):
	post = None
	if TextPost.objects.filter(id=post_id).count() != 0:
		post = TextPost.objects.filter(id=post_id)
	elif ImagePost.objects.filter(id=post_id).count() != 0:
		post = ImagePost.objects.get(id=post_id)

	post.publish()
	page = post.publish_to.all()[0]
	page.Respond(random.choice(Message.objects.filter(payment_succeeded= True)).toJson(int(post.creator_fbid)))

	return render(request, "success.html")

def failed(request):
	return render(request, "failed.html")
def test(request):
	return render(request, "test.html")
def getDates(reach_time,nop):
	schedule_weekday = None
	scheduling_days = []
	if(reach_time.day == "Monday"):
		schedule_weekday = 0
	elif(reach_time.day == "Tuesday"):
		schedule_weekday = 1
	elif(reach_time.day == "Wednesday"):
		schedule_weekday = 2
	elif(reach_time.day == "Thursday"):
		schedule_weekday = 3
	elif(reach_time.day == "Friday"):
		schedule_weekday = 4
	elif(reach_time.day == "Saturday"):
		schedule_weekday = 5
	elif(reach_time.day == "Sunday"):
		schedule_weekday = 6

	scheduling_day  = datetime.today() + timedelta( (schedule_weekday-datetime.today().weekday()) % 7 )
	scheduling_day = scheduling_day.replace(hour = reach_time.time.hour , minute = reach_time.time.minute, second = 0)
	scheduling_days.append(scheduling_day)
	for i in range(nop-1):
		scheduling_days.append(scheduling_day + timedelta(days = 7))
		scheduling_day = scheduling_day + timedelta(days = 7)
	return scheduling_days
