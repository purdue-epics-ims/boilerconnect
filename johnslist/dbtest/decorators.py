from django.http import HttpResponseRedirect
from .models import *


def user_in_group(func):
	def wrapper(request,*args,**kwargs):
		organization_id = kwargs['organization_id']
		members = Organization.objects.get(id=organization_id).members
		if request.user in members:
			return func(request,*args,**kwargs)
		else:
			return HttpResponseRedirect('/')
	return wrapper
