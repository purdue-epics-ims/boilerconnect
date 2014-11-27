from django.shortcuts import render
from johnslist.settings import REDIRECT_URL
from .models import *

#checks that a user is a member or admin of a specific organization
#or, checks that a user is the creator of a job
#or, checks that a user has a user_id

def user_has_object(func):
	def wrapper(request,*args,**kwargs):
		success = False
		if 'organization_id' in kwargs.keys():
			organization = Organization.objects.get(id=kwargs['organization_id'])
			if organization.members.filter(id=request.user.id).exists():
				success = True

		elif 'job_id' in kwargs.keys():
			job = Job.objects.get(id=kwargs['job_id'])
			if request.user.id == job.creator.id:
				success = True

		elif 'user_id' in kwargs.keys():
			user = User.objects.get(id=kwargs['user_id'])
			if request.user.id == user.id:
				success = True

		if success == True:
			return func(request,*args,**kwargs)
		else:
			return render(request,'dbtest/confirm.html',{'title':'Permission Denied','message':'You do not have access to this resource'})
	return wrapper
