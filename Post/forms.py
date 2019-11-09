from django import forms
from .models import * 
from django.core.exceptions import ValidationError
from django.forms import ModelForm

class ImagePostForm(forms.ModelForm):
	class Meta:
		model = ImagePost
		fields = "__all__"

	def clean(self):
		image_url = self.cleaned_data.get('image_url')
		image = self.cleaned_data.get('image')

		if image is not None and image_url is not None:
			raise ValidationError(
					'You Cannot add both image url and uploaded an image'
				)

COUNT = (
	('1', '1'),
	('2', '2'),
	('3', '3'),
	('4', '4'),
	)

class ReachTimeForm(forms.ModelForm):
	reach_time = forms.ModelChoiceField(queryset= ReachTime.objects.all(), empty_label=None, widget=forms.Select(attrs={'class':'form-control'}))
	class Meta:
		model = ReachTime
		fields = ['day','time']

class PaymentForm(forms.Form):
	nop = forms.CharField(max_length=100,widget=forms.Select(attrs={'class':'form-control'},choices= COUNT))
