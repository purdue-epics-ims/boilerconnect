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
	jobs = Organization.objects.get(id=organization_id).accepted.all()
	return render(request, 'dbtest/organization_detail.html',{'organization': organization,'jobs':jobs})

def organization_job_index(request,organization_id):
	organization = Organization.objects.get(id=organization_id)
	return render(request, 'dbtest/organization_job_index.html',{'organization': organization})

def organization_accept_job(request,organization_id):
	organization = Organization.objects.get(id=organization_id)
	print 'lkj'
	if request.method == 'POST':
		print request.POST['job_id']
		job = Job.objects.get(id=request.POST['job_id'])
		job.accepted.add(organization)
		return render(request, 'dbtest/confirm.html',{'title':'Job acceptance','message':'You have accepted the job: {0}'.format(job.name)})

	jobs = organization.requested.all()
	return render(request, 'dbtest/organization_accept_job.html',{'organization': organization,'jobs':jobs})


def job_detail(request,job_id):
	job = Job.objects.get(id=job_id)
	return render(request, 'dbtest/job_detail.html',{'job': job})

def front_page(request):
	return render(request, 'dbtest/front_page.html')

def search(request):
	search = request.GET['search']
	search_result = Organization.objects.filter(name__icontains=search) 
	return render(request,'dbtest/search.html',{'search_result': search_result})
def joblist(request,user_id):
	job_created = User.objects.get(id=user_id).creator
	return render(request,'dbtest/joblist.html',{'job_created':job_created})

def user_create(request):
	#if this request was a POST and not a GET
	if request.method == 'POST':
		form = UserCreateForm(request.POST)
		print form.is_valid()
		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			#	Creating new user in database
			numUsers = User.objects.filter( name = username ).count()
			if numUsers == 0:
				#	Create new user object
				newUser = User ( name = username, password = password )
				#	Save object to database
				newUser.save()
				#	Displays confirmation page
				title = "User {0} created".format( username )
				return render(request,'dbtest/confirm.html', {'title': title,'message':'Thank you for creating an account'})
			else:
				#	Error message if user already exists
				error = "Username {0} already exists in database".format( username )
				return render(request, 'dbtest/user_create.html', {'error' : error })
		else:
			return render(request, 'dbtest/user_create.html', {'form':form,'error':"There are incorrect fields"})
	
	#if the request was a GET
	else:
		form = UserCreateForm()
		return render(request, 'dbtest/user_create.html', {'form':form})
		#try to load the username and pass from the post request
