from django.shortcuts import render
from johnslist.settings import REDIRECT_URL
from .models import *

#general purpose decorator to check if user can access various objects
def user_has_object(func):
	def wrapper(request,*args,**kwargs):
		success = False

		#check if user is member or admin of organization
		if 'organization_id' in kwargs.keys():
			organization = Organization.objects.get(id=kwargs['organization_id'])
			if request.user.has_perm('view_organization',organization) and organization.group.user_set.filter(id=request.user.id).exists():
				success = True

		#or, check if user is creator of job
		elif 'job_id' in kwargs.keys():
			job = Job.objects.get(id=kwargs['job_id'])
			if request.user.id == job.creator.id:
				success = True

		#or, check if user has user_id
		elif 'user_id' in kwargs.keys():
			user = User.objects.get(id=kwargs['user_id'])
			if request.user.id == user.id:
				success = True

		if success == True:
			return func(request,*args,**kwargs)
		else:
			return render(request,'dbtest/confirm.html',{'title':'Permission Denied','message':'You do not have access to this resource'})
	return wrapper
