from django.shortcuts import render
from dbtest.models import *
from django.http import HttpResponse

'''
Views to be written:
	user_detail - show user info
		contact
		name
	organization_detail - show organization info
		name
	organization_job_index - list organizations jobs
		list accepted/requested jobs
		for requested, link to 'accept job'
	job_detail - show job info
		creator, name, description
		link to user profile

	create user - create a User
	create job - create a Job
	add_member - add User to Organization 'members' field
	accept_job - add Organization to to Job 'accepted' field
	organization_search

	front page
	user login - login page for users

todo
	use get_object_or_404 for database lookups
'''

def user_detail(request,user_id):
	user = User.objects.get(id=user_id)
	return render(request, 'dbtest/user_detail.html',{'user': user})

def organization_detail(request,organization_id):
	organization = Organization.objects.get(id=organization_id)
	return render(request, 'dbtest/organization_detail.html',{'organization': organization})

def organization_job_index(request,organization_id):
	organization = Organization.objects.get(id=organization_id)
	return render(request, 'dbtest/organization_job_index.html',{'organization': organization})

def job_detail(request,job_id):
	job = Job.objects.get(id=job_id)
	return render(request, 'dbtest/job_detail.html',{'job': job})

def front_page(request):
	return render(request, 'dbtest/front_page.html')

def create_user(request):
	#if this request was a POST and not a GET
	if request.method == 'POST':
		#try to load the username and pass from the post request
		try:
			username = request.POST['username']
			password = request.POST['password']
			
			#	Creating new user in database
			numUsers = User.objects.filter( name = username ).count()
			
			#	Check if user already exists
			if numUsers == 0:
				#	Create new user object
				newUser = User ( name = username, password = password )
				#	Save object to database
				newUser.save()
			else:
				#	Error message if user already exists
				error = "Username {0} already exists in database".format( username )
				return render(request, 'dbtest/create_user.html', {'error' : error })
			#if there was a KeyError (nonexistant)
		except KeyError:
			#then set the 'error' variable to something and show the create_user page
			return render(request, 'dbtest/create_user.html', {'error':"There are incorrect fields"})
			#if everything worked out fine
		else:
			
			#	Displays confirmation page
			title = "User {0} created".format( username )
			return render(request,'dbtest/confirm.html', {'title': title	})
	
	#if the request was a GET
	else:
		return render(request, 'dbtest/create_user.html')
