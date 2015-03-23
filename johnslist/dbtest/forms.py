from django.db import models
from django.forms import ModelForm,PasswordInput
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
			fields = ['name','description','duedate', 'categories']



