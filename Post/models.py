from django.db import models
import os
from subprocess import Popen, PIPE, STDOUT
import json
import requests
import re 


class ReachTime(models.Model):
	DAYS_OF_WEEK = (
    ("Monday", 'Monday'),
    ("Tuesday", 'Tuesday'),
    ("Wednesday", 'Wednesday'),
    ("Thursday", 'Thursday'),
    ("Friday", 'Friday'),
    ("Saturday", 'Saturday'),
    ("Sunday", 'Sunday'),
	)
	day  = models.CharField(max_length=20,choices= DAYS_OF_WEEK)
	time = models.TimeField()


	def __str__(self):
		return "{} {}".format(self.day,str(self.time))

	class Meta:
		verbose_name = "Reach Time"
		verbose_name_plural = "Reach Times"





class Time(models.Model):
	time = models.DateTimeField()

	def __str__(self):
		return str(self.time)



class Post(models.Model):
	post_label = models.CharField(max_length= 45)
	creator_fbid = models.CharField(max_length= 45,blank = True)
	post_fbid = models.CharField(max_length = 255,blank = True)
	publish_to = models.ManyToManyField('Page.Page',blank = True)
	publish_at = models.ManyToManyField(Time,blank= True)

	def __str__(self):
		return self.post_label


class TextPost(Post):
	post_text = models.TextField()
	post_url  = models.CharField(max_length = 500,blank= True)

	def filter(self):
		wordList = re.sub("[^\w]", " ",  self.post_text).split()
		valid = True
		for word in wordList:
			bad_word = Filter.objects.filter(word= word.lower()).count()
			if bad_word != 0 :
				valid = False
				break
		return valid

	def categorize(self):
		wordList = re.sub("[^\w]", " ",  self.post_text).split()
		category = None
		for word in wordList:
			try:
				category_qs = Category.objects.get(words__word= word.lower())
				category = category_qs.category 
				break
			except:
				pass
		return category
				

	def publish(self,category=None):
		if category is not None:
			post_text = "#{}\n {}".format(category.upper(),self.post_text)
		else:
			post_text = self.post_text

		count = self.publish_at.all().count()
		if count == 0:
			for page in self.publish_to.all():
				post_url = "https://graph.facebook.com/{}/feed?access_token={}".format(page.page_fbid,page.page_token)
				if self.post_url == "":
					print("it is null")
					params = json.dumps({
        	          "message": post_text
        	       })
				else:
					print("it is not null")
					params = json.dumps({
        	          "message":post_text, 
        	          "link":self.post_url
        	       })
				
				status = requests.post(post_url, headers={"Content-Type": "application/json"},data=params)
				if self.publish_to.all().count() == 1 :
					return status.json()
		else:
			for page in self.publish_to.all():
				for time in self.publish_at.all():
					if self.post_url is None:
						params = json.dumps({
							"published": False, 
							"message": post_text, 
							"scheduled_publish_time":str(time.time).replace("","T")
							})
					else:
						params = json.dumps({
							"published": False, 
							"message":post_text, 
							"link":self.post_url, 
							"scheduled_publish_time":str(time.time).replace(" ","T")
							})
					print(params)
					post_url = "https://graph.facebook.com/{}/feed?access_token={}".format(page.page_fbid,page.page_token)
					status = requests.post(post_url, headers={"Content-Type": "application/json"},data=params)
					print(status.json())

	def delete(self):
		page = self.publish_to.all()[0]
		status = requests.delete("https://graph.facebook.com/{}?access_token={}".format(self.post_fbid,page.page_token))

	class Meta: 
		verbose_name = "Text post"
		verbose_name_plural = "Text posts"

class ImagePost(Post):
	image_caption = models.TextField()
	image_url = models.URLField(max_length = 500,blank = True)
	image = models.ImageField(upload_to = "images/",null= True,blank= True)

	def filter(self):
		wordList = re.sub("[^\w]", " ",  self.image_caption).split()
		valid = True
		for word in wordList:
			bad_word = Filter.objects.filter(word= word.lower()).count()
			if bad_word != 0 :
				valid = False
				break
		return valid

	def categorize(self):
		wordList = re.sub("[^\w]", " ",  self.image_caption).split()
		category = None
		for word in wordList:
			try:
				category_qs = Category.objects.get(words__word= word.lower())
				category = category_qs.category 
				break
			except:
				pass
		return category

	def publish(self,category=None):
		count = self.publish_at.all().count()
		if count == 0:
			for page in self.publish_to.all():
				if self.image_caption == "":
					params = json.dumps({
						"url":self.image_url
					})
				else:
					if category is not None:
						image_caption = "#{}\n{}".format(category,self.image_caption)
					else:
						image_caption = self.image_caption
					params = json.dumps({
						"url":self.image_url, 
						"caption":image_caption
					})
				post_url = "https://graph.facebook.com/{}/photos?access_token={}".format(page.page_fbid,page.page_token)
				status = requests.post(post_url, headers={"Content-Type": "application/json"},data=params)
				if self.publish_to.all().count() == 1 :
					return status.json()
		else:
			for page in self.publish_to.all():
				post_url = "https://graph.facebook.com/{}/photos?access_token={}".format(page.page_fbid,page.page_token)
				for time in self.publish_at.all():
					if self.image_caption == "":
						params = json.dumps({
							"published":False,
							"url":self.image_url,
							"scheduled_publish_time":int(time.time.timestamp()),
						})
					else:
						if category is not None:
							image_caption = "#{}\n{}".format(category,self.image_caption)
						else:
							print(int(time.time.timestamp()))
							print(type(time.time.timestamp()))
							image_caption = self.image_caption
							params = json.dumps({
							"published":False,
							"url":self.image_url, 
							"caption":image_caption,
							"scheduled_publish_time":int(time.time.timestamp()),
					})
					status = requests.post(post_url, headers={"Content-Type": "application/json"},data=params)
					print(status.json())



	def delete(self):
		page = self.publish_to.all()[0]
		status = requests.delete("https://graph.facebook.com/{}?access_token={}".format(self.post_fbid,page.page_token))

	class Meta:
		verbose_name = "Image post"
		verbose_name_plural = "Image posts"

class Filter(models.Model):
	word = models.CharField(max_length= 255)
	def save(self, *args, **kwargs):
		self.word = self.word.lower()
		return super(Filter, self).save(*args, **kwargs)
	def __str__(self):
		return self.word

class Word(models.Model):
	word = models.CharField(max_length= 255)
	def save(self, *args, **kwargs):
		self.word = self.word.lower()
		return super(Word, self).save(*args, **kwargs)
	def __str__(self):
		return self.word

class Category(models.Model):
	category = models.CharField(max_length= 255)
	words = models.ManyToManyField(Word)


	def __str__(self):
		return self.category

	class Meta:
		verbose_name = "Category"
		verbose_name_plural = "Categories"