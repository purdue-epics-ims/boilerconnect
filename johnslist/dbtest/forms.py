from django.db import models
from django.forms import ModelForm,PasswordInput,Textarea
from django.contrib.auth.models import User
from django.contrib.auth import forms
from .models import*
class OrganizationCreateForm(ModelForm): 
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
        exclude = ('jobrelation',)
