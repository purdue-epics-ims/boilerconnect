from django.shortcuts import render
from .models import *
from django.http import HttpResponse
from django.contrib.auth.views import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
import random
from .decorators import *
'''
	user_detail - show user info
		contact
		name
	organization_detail - show organization info
		name
	organization_job_index - list organizations jobs
		list accepted/requested jobs
		for requested, link to 'accept job'
	organization_accept_job - members/admin can accept organization jobs
	job_detail - show job info
		creator, name, description
		link to user profile
	front_page - organization search, logo, organization showcase
	search - search results for search on front_page
	user_job_index - list of jobs user has created
	user_membership - list of organizations user is part of

	user_create
	organization_create
	job_create

todo
	add_member - add User to Organization 'members' field
	use get_object_or_404 for database lookups
'''

@user_has_object
def user_detail(request,user_id):
	user = User.objects.get(id=user_id)
	return render(request, 'dbtest/user_detail.html',{'user': user})

def organization_detail(request,organization_id):
	organization = Organization.objects.get(id=organization_id)
	jobs = Organization.objects.get(id=organization_id).accepted.all()
	return render(request, 'dbtest/organization_detail.html',{'organization': organization,'jobs':jobs})

@user_has_object
def organization_job_index(request,organization_id):
	organization = Organization.objects.get(id=organization_id)
	return render(request, 'dbtest/organization_job_index.html',{'organization': organization})

@user_has_object
def organization_accept_job(request,organization_id):
	organization = Organization.objects.get(id=organization_id)
	if request.method == 'POST':
		job = Job.objects.get(id=request.POST['job_id'])
		job.accepted.add(organization)
		job.requested.remove(organization)
		return render(request, 'dbtest/confirm.html',{'title':'Job acceptance','message':'You have accepted the job: {0}'.format(job.name)})

	jobs = organization.requested.all()
	return render(request, 'dbtest/organization_accept_job.html',{'organization': organization,'jobs':jobs})

def job_detail(request,job_id):
	job = Job.objects.get(id=job_id)
	return render(request, 'dbtest/job_detail.html',{'job': job})

def front_page(request):
	count = Organization.objects.count()
	random_num1 = random.randint(1,count)
	org1 = Organization.objects.get(id = random_num1)
	random_num2 = random.randint(1,count)
	while random_num2 == random_num1:
		random_num2 = random.randint(1,count)

	org2 = Organization.objects.get(id = random_num2)
	random_num3 = random.randint(1,count)
	while random_num3 == random_num1 or random_num3 == random_num2:
		random_num3 = random.randint(1,count)

	org3 = Organization.objects.get(id = random_num3)
	organizations = [org2, org3]
	return render(request, 'dbtest/front_page.html',{'active_organization':org1,'organizations':organizations})

def search(request):
	search = request.GET['search']
	search_result = Organization.objects.filter(name__icontains=search) 
	return render(request,'dbtest/search.html',{'search_result': search_result})

@user_has_object
def user_job_index(request,user_id):
	jobs = User.objects.get(id=user_id).creator
	return render(request,'dbtest/user_job_index.html',{'jobs':jobs})

@user_has_object
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

def user_edit(request):
        #if this request was a POST and not a GET
        args = {}
	if request.method == 'POST':
		form = UserCreationForm(request.POST, instance=request.user)
                form.actual_user = request.user

		#check form validity
		if form.is_valid() :
			#save user to db and store info to 'user'
			user = form.save(commit = False)
                        #user.username = request.user.username()
			title = "User {0} modified".format( user.username )
			message = "Your account has been modified."
                        user.save()
			return render(request,'dbtest/confirm.html', {'title': title,'message':message})
		else:
			return render(request, 'dbtest/user_edit.html', {'form':form,'error':"There are incorrect fields"})
	#if the request was a GET
	else:
		form = UserCreationForm()
                args['form'] = form
		return render(request, 'dbtest/user_edit.html', args)

def organization_edit(request):
        #if this request was a POST and not a GET
        args = {}
	if request.method == 'POST':
		form = OrganizationCreateForm(request.POST, instance=request.organization)
                form.actual_organization = request.organization

		#check form validity
		if form.is_valid() :
			#save organization to db and store info to 'organization'
			organization = form.save(commit = False)
			title = "Organization {0} modified".format( organization.username )
			message = "Your account has been modified."
                        organization.save()
			return render(request,'dbtest/confirm.html', {'title': title,'message':message})
		else:
			return render(request, 'dbtest/organization_edit.html', {'form':form,'error':"There are incorrect fields"})
	#if the request was a GET
	else:
		form = OrganizationCreateForm()
                args['form'] = form
		return render(request, 'dbtest/organization_edit.html', args)


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

