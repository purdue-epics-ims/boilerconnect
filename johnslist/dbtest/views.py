from django.shortcuts import render,get_object_or_404,redirect
from .models import *
from django.http import HttpResponseRedirect
from django.contrib.auth.views import login as auth_login
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
import random
from django.forms.models import inlineformset_factory
from .decorators import user_has_perm
from .forms import*
from guardian.shortcuts import assign_perm
from notifications import notify

#login with provided user/pass
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth_login(request, user)
            return redirect('front_page')
        else:
            error = "There was a problem with your login.  Please try again." 
            return render(request,'dbtest/login.html',{'error':error})
    if request.method == 'GET':
        return render(request,'dbtest/login.html')

#get detailed user information - email, phone number, Orgs they are part of, etc.
# users don't have any permissions right now, so just check that request.user == user
@user_has_perm('foobar')
def user_detail(request,user_id):
    user = get_object_or_404(User,id=user_id)
    return render(request, 'dbtest/user_detail.html',{'user_detail': user})

#a list of a user's notifications
def notifications(request):
    read_notifications = request.user.notifications.read()
    unread_notifications = list(request.user.notifications.unread())
    request.user.notifications.mark_all_as_read()
    return render(request, 'dbtest/notifications.html', {'unread_notifications' : unread_notifications,'read_notifications':read_notifications})

#get detailed organization information - email, phone #, users in Org, admins, etc.
def organization_detail(request,organization_id):
    organization = Organization.objects.get(id=organization_id)
    jobs = organization.jobs_pending()
    admins = organization.get_admins()
    
    return render(request, 'dbtest/organization_detail.html',
                {'organization': organization,
                 'jobs':jobs,
                 'admins':admins,
                 'members':organization.group.user_set.all(),
                 })

#get a list of an Org's jobs
@user_has_perm('view_organization')
def organization_job_index(request,organization_id):
    organization = Organization.objects.get(id=organization_id)
    return render(request, 'dbtest/organization_job_index.html',{'organization': organization})


#accept or decline a requested Job
@user_has_perm('is_admin')
def organization_accept_job(request,organization_id):
    org = Organization.objects.get(id=organization_id)
    if request.method == 'POST':
        job = Job.objects.get(id=request.POST['job_id'])
        jr = JobRequest.objects.get(job=job,organization = org)
        if request.POST.get("action","") == "Accept Job":
            if jr.accepted is False or jr.declined is False:
                jr.accepted = True
                jr.save()
            else:
                return render(request,'dbtest/organization_accept_job.html',{'orgnanization':org,'error':'you have already accepted/declined the job'})
            for user_org in org.group.user_set.all():
                notify.send(request.user, recipient = user_org, verb = 'accepted your job')
            return render(request, 'dbtest/confirm.html',{'title':'Job acceptance','message':'You have accepted the job: {0}'.format(job.name)})  
        if request.POST.get("action","") == "Decline Job":
            if jr.accepted is False or jr.declined is False:
                jr.declined = True
                jr.save()
            else:
                return render(request,'dbtest/organization_accept_job.html',{'orgnanization':org,'error':'you have already accepted/declined the job'})
            for user_org in org.group.user_set.all():
                notify.send(request.user, recipient = user_org, verb = 'declined your job')
            return render(request, 'dbtest/confirm.html',{'title':'Job decline','message':'You have declined the job: {0}'.format(job.name)})  
    return render(request, 'dbtest/organization_accept_job.html',{'organization': org})

#get detailed info about a job
@user_has_perm('view_jobrequest')
def job_detail(request,job_id,organization_id):
    job = Job.objects.get(id=job_id)
    organization = Organization.objects.get(id=organization_id)
    jobrequest = JobRequest.objects.get(job = job, organization = organization);
    comment_text = jobrequest.comment_set.all()
    if request.method == 'POST':
        form = CommentCreateForm(request.POST)
        if form.is_valid():
            comment = form.save(commit = False)
            comment.jobrequest = jobrequest
            comment.save()
            return render(request, 'dbtest/confirm.html',{'title':'comment saved!','message':'You have saved the comment to {0}'.format(job.name)})  
        else:
            return render(request, 'dbtest/job_detail.html', {'jobrequest':jobrequest,'form':form,'error': 'The comment cannot be empty!','comment_text':comment_text})

    return render(request, 'dbtest/job_detail.html',{'jobrequest':jobrequest,'comment_text':comment_text})

#load the front page with 3 random organizations in the gallery
def front_page(request):
    orgs = Organization.objects.all()
    if(len(orgs) >= 3):
        orgs = random.sample(orgs,3)
        return render(request, 'dbtest/front_page.html',{'active_organization':orgs[0],'organizations':orgs[1:]})
    else:
        return render(request, 'dbtest/front_page.html')

def search(request):
    search_result=[]

    search = request.GET['search'] # the provided search string
    search_model = request.GET['search_model'] # the kind of object returned by the search
    search_by = request.GET['search_by'] # where to apply the search string

    if search_model.lower() == 'organization':
        if search_by.lower() == 'category':
            category = Category.objects.get(name=search)
            search_result = category.organization_set.all()
        if search_by.lower() == 'name':
            search_result = Organization.objects.filter(name__icontains=search)
            
    return render(request,'dbtest/search.html',{'search_result': search_result})


@user_has_perm('view_user')
def user_job_index(request,user_id):
    jobs = User.objects.get(id=user_id).creator
    return render(request,'dbtest/user_job_index.html',{'jobs':jobs})

@user_has_perm('view_user')
def user_membership(request,user_id):
    membership = User.objects.get(id = user_id).groups
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

@login_required
def organization_create(request):
    #if this request was a POST and not a GET
    if request.method == 'POST':
        form = OrganizationCreateForm(request.POST)

        #check form validity
        if form.is_valid() :
            #create new org 
            organization = form.save(commit=False)
            group = Group.objects.create(name = organization.name)
            organization.group = group
            group.user_set.add(request.user)
            organization.icon = request.FILES['icon']
            organization.save()
            form.save_m2m()
            #set the admin to user1 organization.admin = User.objects.get(id=1)
            assign_perm('is_admin',request.user, organization)

            title = "Organization {0} created".format( organization.name )
            message = "Thank you for creating an organization."
            return render(request,'dbtest/confirm.html', {'title': title,'message':message})
        else:
            return render(request, 'dbtest/organization_create.html', {'form':form,'error':"There are incorrect fields"})
    #if the request was a GET
    else:
        form = OrganizationCreateForm()
        return render(request, 'dbtest/organization_create.html', {'form':form})

@login_required
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
        if request.user.is_authenticated():
            form = UserCreationForm(instance=request.user)
        else:
            form = UserCreationForm()
        return render(request, 'dbtest/user_edit.html', 
            {'form':form}
            )

@login_required
@user_has_perm('edit_organization')
def organization_edit(request, organization_id):
    print organization_id
    organization = Organization.objects.get(id=organization_id)
    print organization
        #if this request was a POST and not a GET
    args = {}
    if request.method == 'POST':
        organization = Organization.objects.get(id=organization_id)
        form = OrganizationCreateForm(request.POST, instance=organization)
        form.actual_organization = organization

        #check form validity
        if form.is_valid() :
            #save organization to db and store info to 'organization'
            organization = form.save(commit = False)
            title = "Organization {0} modified".format( organization.name )
            message = "Organization {0} has been modified.".format(organization.name)
            organization.save()
            return render(request,'dbtest/confirm.html', {'title': title,'message':message})
        else:
            return render(request, 'dbtest/organization_edit.html', {'form':form,'error':"There are incorrect fields", 'organization_id': organization_id})
    #if the request was a GET
    else:
        organization = Organization.objects.get(id=organization_id)
        form = OrganizationCreateForm(request.POST, instance=organization)
        return render(request, 'dbtest/organization_edit.html', {'form':form,'organization_id' : organization_id})

@login_required
def job_create(request):
    #if this request was a POST and not a GET
    if request.method == 'POST':
        form = JobCreateForm(request.POST)
        #check form validity
        if form.is_valid():
            job = form.save(commit=False)
            job.creator = request.user
            job.save()
            #get the list of orgs to request from the form
            for org in request.POST.getlist('organization'):
                organization = Organization.objects.get(id = org)
                JobRequest.objects.create(organization=organization, job = job)
                for user in organization.group.user_set.all():
                    notify.send(request.user, recipient = user, verb = 'sent {0} a job request'.format(organization.name))
            #get the list of categories from the form
            for cat in request.POST.getlist('categories'):
                job.categories.add(Category.objects.get(id=cat))
                job.save()
            title = "Job {0} created".format( job.name )
            message = "Thank you for creating the job."
            return render(request,'dbtest/confirm.html', {'title': title,'message':message})
        else:
            return render(request, 'dbtest/job_create.html', {'form':form,'error':"There are incorrect fields"})
    #if the request was a GET
    else:
        form = JobCreateForm()
        return render(request, 'dbtest/job_create.html', {'form':form})

def about(request):
    return render(request, 'dbtest/about.html')
