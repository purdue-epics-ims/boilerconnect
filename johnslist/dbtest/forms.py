from django.db import models
from django import forms
from django.forms import ModelForm,PasswordInput,Textarea
from django.contrib.auth.models import User
from django.contrib.auth import forms
from .models import*

class OrganizationCreateForm(ModelForm):
	def __init__(self, *args, **kwargs):
			super(OrganizationCreateForm, self).__init__(*args, **kwargs)
			self.fields['name'].widget.attrs.update({'type': 'text', 'class' : 'form-control', 'placeholder' : 'What\'s the name of the organization?', 'autofocus' : 'true'})
			self.fields['description'].widget.attrs.update({'type': 'text','class' : 'form-control'})
			self.fields['categories'].widget.attrs.update({'class' : 'form-control'})
			self.fields['icon'].widget.attrs.update({'class' : 'form-control'})


	class Meta:
		model = Organization
		fields = ['name','description','categories','icon']

class JobCreateForm(ModelForm):
    class Meta:
        model = Job
        exclude = ('creator',)
	
class CommentCreateForm(ModelForm):
    class Meta:
        model = Comment
        exclude = ('jobrequest',)

