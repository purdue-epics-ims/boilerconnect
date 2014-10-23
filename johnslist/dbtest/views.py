from django.http import HttpResponse
from dbtest.models import *
from django.template import RequestContext, loader
	
'''
Basic views to be written:
	- index page which can list each kind of entity (Organizations, Users, Jobs, and Service Categories
	- details page for each entity - most important right now is Organization page
	- login page
'''

def organization_index(request):
	return HttpResponse(Organization.objects.all())	

def job_index(request):
	return HttpResponse(Job.objects.all())

def user_index(request):
	user_list = User.objects.all()

	template = loader.get_template('dbtest/index.html')
	context = RequestContext(request, {
		'users': user_list,
	})
	return HttpResponse(template.render(context))
