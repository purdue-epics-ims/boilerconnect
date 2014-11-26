from django.shortcuts import render
from .models import *
from django.http import HttpResponse
from django.contrib.auth.views import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
import random
from .decorators import *
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
	create Organiation - create an organization
	add_member - add User to Organization 'members' field
	accept_job - add Organization to to Job 'accepted' field
	organization_search

	front page
	user login - login page for users

todo
	use get_object_or_404 for database lookups
	use django login view to handle logins
'''

@login_required
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

@user_in_organization
def organization_accept_job(request,organization_id):
	organization = Organization.objects.get(id=organization_id)
	if request.method == 'POST':
		job = Job.objects.get(id=request.POST['job_id'])
		job.accepted.add(organization)
		return render(request, 'dbtest/confirm.html',{'title':'Job acceptance','message':'You have accepted the job: {0}'.format(job.name)})

	jobs = organization.requested.all()
	return render(request, 'dbtest/organization_accept_job.html',{'organization': organization,'jobs':jobs})

def job_detail(request,job_id):
	job = Job.objects.get(id=job_id)
	return render(request, 'dbtest/job_detail.html',{'job': job})

def front_page(request):
	count = Job.objects.count()
	random_num = random.randint(1,count)
	showcase = Job.objects.get(id = random_num)
	return render(request, 'dbtest/front_page.html',{'showcase': showcase})

def search(request):
	search = request.GET['search']
	search_result = Organization.objects.filter(name__icontains=search) 
	return render(request,'dbtest/search.html',{'search_result': search_result})

def user_job_index(request,user_id):
	jobs = User.objects.get(id=user_id).creator
	return render(request,'dbtest/user_job_index.html',{'jobs':jobs})

def user_membership(request,user_id):
	membership = User.objects.get(id = user_id).members
	return render(request,'dbtest/user_membership.html',{'membership': membership})

def user_create(request):
	#if this request was a POST and not a GET
	if request.method == 'POST':
		form = UserCreationForm(request.POST)

		#check form validity
		if form.is_valid() :
			#save user to db and store info to 'user'
			user = form.save()
			form.save_m2m()
			title = "User {0} created".format( user.username )
			message = "Thank you for creating an account."
			return render(request,'dbtest/confirm.html', {'title': title,'message':message})
		else:
			return render(request, 'dbtest/user_create.html', {'form':form,'error':"There are incorrect fields"})
	#if the request was a GET
	else:
		form = UserCreationForm()
		return render(request, 'dbtest/user_create.html', {'form':form})

def organization_create(request):
	#if this request was a POST and not a GET
	if request.method == 'POST':
		form = OrganizationCreateForm(request.POST)

		#check form validity
		if form.is_valid() :
			organization = form.save(commit=False)
			#set the admin to user1 organization.admin = User.objects.get(id=1)
			organization.admin = request.user
			#create new org 
			organization.save()
			form.save_m2m()
			title = "Organization {0} created".format( organization.name )
			message = "Thank you for creating an organization."
			return render(request,'dbtest/confirm.html', {'title': title,'message':message})
		else:
			return render(request, 'dbtest/organization_create.html', {'form':form,'error':"There are incorrect fields"})
	#if the request was a GET
	else:
		form = OrganizationCreateForm()
		return render(request, 'dbtest/organization_create.html', {'form':form})

def job_create(request):
	#if this request was a POST and not a GET
	if request.method == 'POST':
		form = JobCreateForm(request.POST)

		#check form validity
		if form.is_valid() :
			job = form.save(commit=False)
			job.creator = User.objects.get(id=1)
			#create new org 
			job.save()
			form.save_m2m()
			title = "Job {0} created".format( job.name )
			message = "Thank you for creating the job."
			return render(request,'dbtest/confirm.html', {'title': title,'message':message})
		else:
			return render(request, 'dbtest/job_create.html', {'form':form,'error':"There are incorrect fields"})
	#if the request was a GET
	else:
		form = JobCreateForm()
		return render(request, 'dbtest/job_create.html', {'form':form})

