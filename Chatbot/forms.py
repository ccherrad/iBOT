from django import forms
from .models import * 
from django.core.exceptions import ValidationError


class MessageForm(forms.ModelForm):
	class Meta:
		model = Message
		fields = "__all__"

	def clean(self):
		buttons = self.cleaned_data.get('buttons')
		if len(buttons) > 3 :
			raise ValidationError(
					'Message cannot hundle more than 3 buttons'
				)
		return self.cleaned_data

class ActionForm(forms.ModelForm):
	class Meta:
		model : Action 
		fields = "__all__"


	def clean(self):
		action_type = self.cleaned_data.get('action_type')
		message = self.cleaned_data.get('message')
		inputs = self.cleaned_data.get('inputs')

		if action_type == "Reply":
			if message is None:
				raise ValidationError('Message is required if action reply')
			elif len(inputs) > 0 :
				raise ValidationError('Reply action must not include any input')
		if action_type == "Input":
			if len(inputs) != 1 :
				raise ValidationError('Action to get user input must contain one input')
			elif message is not None:
				raise ValidationError('Input has a placeholder no need for additional text')
		if action_type == "Publish":
			if len(inputs) == 0: 
				raise ValidationError('Please provide what to publish')
