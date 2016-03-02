from django.shortcuts import render,get_object_or_404,redirect
from .models import *
from django.http import HttpResponseRedirect
from django.contrib.auth.views import login as auth_login
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
import random
from django.forms.models import inlineformset_factory
from .decorators import user_has_perm, user_is_type
from .forms import*
from guardian.shortcuts import assign_perm
from notifications import notify
from django.core.mail import send_mail

def quicksearch(request):
    orgs = Organization.objects.all()
    return render(request,'dbtest/quicksearch.html',
                {'orgs':orgs})

#determine if this is the first time a user has visited a page
def first_visit(user,view):
    if view not in user.userprofile.visited_views:
        user.userprofile.visited_views += "{0},".format(view)
        user.userprofile.save()
        return True
    else:
        return False

#login with provided user/pass
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth_login(request, user)
            return redirect('user_dash')
        else:
            error = "There was a problem with your login.  Please try again." 
            return render(request,'dbtest/login.html',{'error':error})
    if request.method == 'GET':
        return render(request,'dbtest/login.html')

@login_required
def user_dash(request):
    user = request.user
    read_notifications = list(request.user.notifications.read())
    unread_notifications = list(request.user.notifications.unread())
    request.user.notifications.mark_all_as_read()

    #If this is the first time the user has visited this page, show a dialog
    show_dialog = first_visit(user,'user_dash')

    if user.userprofile.purdueuser:
        orgs = [group.organization for group in user.groups.all()]
        return render(request,
                      'dbtest/purdueuser_dash.html',
                      {'user_dash': user,
                       'organizations':orgs,
                       'unread_notifications':unread_notifications,
                       'read_notifications':read_notifications,
                       'show_dialog':show_dialog
                       })
    else:
        jobs = user.jobs.all()
        return render(request, 'dbtest/communitypartner_dash.html',
                     {'user_dash': user,
                       'jobs':jobs,
                       'unread_notifications':unread_notifications,
                       'read_notifications':read_notifications,
                       'show_dialog':show_dialog
                     })

#display job information, show jobrequests and their current state
@user_is_type('communitypartner')
@user_has_perm('view_job')
def job_dash(request,job_id):
    #If this is the first time the user has visited this page, show a dialog
    show_dialog = first_visit(request.user,'job_dash')

    job = Job.objects.get(id=job_id)
    return render(request, 'dbtest/job_dash.html',
                  {'job':job,
                   'jobrequests':job.jobrequests.order_by('organization'),
                   'show_dialog':show_dialog
                  })

#a list of a user's notifications
def notifications(request):
    read_notifications = list(request.user.notifications.read())
    unread_notifications = list(request.user.notifications.unread())
    request.user.notifications.mark_all_as_read()
    return render(request, 'dbtest/notifications.html', {'unread_notifications' : unread_notifications,'read_notifications':read_notifications})

#get detailed organization information - email, phone #, users in Org, admins, etc.
def organization_detail(request,organization_id):
    organization = Organization.objects.get(id=organization_id)
    jobs = organization.jobrequests_pending()
    admins = organization.get_admins()
    return render(request, 'dbtest/organization_detail.html',
                {'organization': organization,
                 'jobs':jobs,
                 'admins':admins,
                 'members':organization.group.user_set.all(),
                 })

#display jobs and members of an organization
@user_is_type('purdueuser')
@user_has_perm('view_organization')
def organization_dash(request,organization_id):
    #If this is the first time the user has visited this page, show a dialog
    show_dialog = first_visit(request.user,'organization_dash')

    org = Organization.objects.get(id=organization_id)
    members = org.group.user_set.all()
    jobrequests = JobRequest.objects.filter(organization=org)
    return render(request, 'dbtest/organization_dash.html',
                  {'organization':org,
                   'members':members,
                   'jobrequests':jobrequests,
                   'show_dialog':show_dialog
                  })

#get detailed info about a jobrequest
@user_has_perm('view_jobrequest')
def jobrequest_dash(request,job_id,organization_id):
    #If this is the first time the user has visited this page, show a dialog
    show_dialog = first_visit(request.user,'jobrequest_dash')

    job = Job.objects.get(id=job_id)
    organization = Organization.objects.get(id=organization_id)
    jobrequest = JobRequest.objects.get(job = job, organization = organization)
    comment_text = jobrequest.comment_set.all()
    perm_to_edit_jobrequest_state = request.user.has_perm('edit_jobrequest_state',jobrequest)
    # if request is a POST
    if request.method == 'POST':
        form = CommentCreateForm(request.POST)

        # handle accept button click
        if request.POST.get("action","")=="Accept Request":
            if jobrequest.is_pending() and perm_to_edit_jobrequest_state:
                jobrequest.accept()
                return render(request, 'dbtest/jobrequest_dash.html',{'perm_to_edit_jobrequest_state':perm_to_edit_jobrequest_state,'comment_text':comment_text,'jobrequest':jobrequest,'confirm':'You have accepted this job.'})
            else:
                return render(request,'dbtest/jobrequest_dash.html',{'perm_to_edit_jobrequest_state':perm_to_edit_jobrequest_state,'comment_text':comment_text,'jobrequest':jobrequest,'error':'You have already accepted/declined the job'})

        # handle decline button click
        if request.POST.get("action","")=="Decline Request":
            if jobrequest.is_pending() and perm_to_edit_jobrequest_state:
                jobrequest.decline()
                return render(request, 'dbtest/jobrequest_dash.html',{'perm_to_edit_jobrequest_state':perm_to_edit_jobrequest_state,'comment_text':comment_text,'jobrequest':jobrequest,'confirm':'You have declined this job.'})
            else:
                return render(request,'dbtest/jobrequest_dash.html',{'perm_to_edit_jobrequest_state':perm_to_edit_jobrequest_state,'comment_text':comment_text,'jobrequest':jobrequest,'error':'you have already accepted/declined this job'})

        if form.is_valid():
            comment = form.save(commit = False)
            comment.creator = request.user
            comment.jobrequest = jobrequest
            comment.save()
            # send notification to either Organization or Community partner
            if request.user.userprofile.purdueuser:
                notify.send(request.user,
                            verb="commented on",
                            action_object=job,
                            recipient=job.creator,
                            url=reverse('jobrequest_dash',kwargs={'organization_id':organization.id,'job_id':job.id}) )
            else:
                notify.send(request.user,
                            verb="commented on",
                            action_object=job,
                            recipient=jobrequest.organization.group,
                            url=reverse('jobrequest_dash',kwargs={'organization_id':organization.id,'job_id':job.id}) )
                return render(request, 'dbtest/jobrequest_dash.html',{'form':form,'comment_text':comment_text,'jobrequest':jobrequest,'confirm':'comment saved!'})
        else:
            return render(request, 'dbtest/jobrequest_dash.html', {'jobrequest':jobrequest,'form':form,'error': 'The comment cannot be empty!','comment_text':comment_text})

    # if request is GET
    return render(request, 'dbtest/jobrequest_dash.html',
            {'jobrequest':jobrequest,'comment_text':comment_text,'show_dialog':show_dialog,'perm_to_edit_jobrequest_state':perm_to_edit_jobrequest_state})

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
def user_membership(request,user_id):
   if(request.user.userprofile.purdueuser):
       membership = User.objects.get(id = user_id).groups
       return render(request,'dbtest/user_membership.html',{'membership': membership})
   else:
       return render(request, 'dbtest/confirm.html',{'error': "You do not have permission to access to this page"})

def user_create(request):
    if request.user.is_authenticated():
        return redirect('user_dash')
    #if this request was a POST and not a GET
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        #check form validity
        if form.is_valid() :
            #save user to db and store info to 'user'
            if request.POST.get('user_type') == "purdue":
                purdue = True
            elif request.POST.get('user_type') == "community":
                purdue = False
            else:
                return render(request, 'dbtest/user_create.html', {'form':form,'error':"There are incorrect fields."})
            user = form.save()
            UserProfile.objects.create(name = user.username, user = user, purdueuser = purdue)
            form.save_m2m()
           
            title = "User {0} created".format( user.username )
            confirm = "Thank you for creating an account."
           # need to do auto login here
           # login_user = authenticate(username=user.username, password=user.password)
           # auth_login(request, login_user)
            return render(request,'dbtest/front_page.html', {'title': title,'confirm':confirm})
        else:
            return render(request, 'dbtest/user_create.html', {'form':form,'error':"There are incorrect fields."})
    #if the request was a GET
    else:
        form = UserCreationForm()
        return render(request, 'dbtest/user_create.html', {'form':form})

@login_required
def organization_create(request):
    #If this is the first time the user has visited this page, show a dialog
    show_dialog = first_visit(request.user,'organization_create')

    #if purdueuser
    if(request.user.userprofile.purdueuser):
        #if the request was a GET
        if request.method == 'GET':
            form = OrganizationCreateForm()
            return render(request, 'dbtest/organization_create.html',
                          {'form':form,'show_dialog':show_dialog})
        #if this request was a POST
        elif request.method == 'POST':
            form = OrganizationCreateForm(request.POST, request.FILES)

            #check form validity
            if form.is_valid() :
                #create new Group + Organization
                organization = form.save(commit=False)
                group = Group.objects.create(name = organization.name)
                organization.group = group
                group.user_set.add(request.user)
                organization.save()
                form.save_m2m()

                message = "Organization {0} created".format( organization.name )
                return render(request,'dbtest/confirm.html', {'confirm':message})
            else:
                return render(request, 'dbtest/organization_create.html', {'form':form,'error':form.errors})
    #if communitypartner
    else:
        return render(request, 'dbtest/confirm.html',
                      {'error': "You do not have permission to access to this page"}
                      )

@login_required
def user_edit(request):
        #if this request was a POST and not a GET
    if request.method == 'POST':
        form = UserCreationForm(request.POST, instance=request.user)
        form.actual_user = request.user

        #check form validity
        if form.is_valid() :
            #save user to db and store info to 'user'
            user = form.save(commit = False)
            #user.username = request.user.username()
            title = "User {0} modified".format( user.username )
            confirm = "Your account has been modified."
            user.save()
            return render(request,'dbtest/user_dash.html', {'title': title,'confirm':confirm})
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
@user_is_type('purdueuser')
@user_has_perm('edit_organization')
def organization_settings(request, organization_id):
    organization = Organization.objects.get(id=organization_id)
    #if the request was a GET
    if request.method == 'GET':
        organization = Organization.objects.get(id=organization_id)
        modelform = OrganizationCreateForm(request.POST, instance=organization)
        categories_id = []
        for category in organization.categories.all():
            categories_id.insert(0, category.pk)
        return render(request, 'dbtest/organization_settings.html', {'modelform':modelform,'organization' : organization, 'categories_id': categories_id})

    elif request.method == 'POST':
        organization = Organization.objects.get(id=organization_id)
        modelform = OrganizationCreateForm(request.POST, instance=organization)
        model_out = modelform.save(commit = False)

        # modelform.actual_organization = organization

        #check modelform validity
        if modelform.is_valid() :
            #get modelform info
            organization = modelform.save(commit = False)
            message = "Organization {0} has been modified.".format(organization.name)
            organization.save()
            return render(request,'dbtest/organization_settings.html',
                            {'confirm':message, 'modelform':modelform, 'organization':organization}
                            )
        else:
            return render(request, 'dbtest/organization_settings.html',
                            {'modelform':modelform,'error':modelform.errors, 'organization': organization}
                            )

@login_required
def job_creation(request):
    if(request.user.userprofile.purdueuser):
        return render(request, 'dbtest/confirm.html',{'error': "You do not have permission to access to this page"})
    else:
       #if this request was a POST and not a GET
       if request.method == 'POST':
           form = JobCreateForm(request.POST)
           #check form validity
           if form.is_valid():
               job = form.save(commit=False)
               job.creator = request.user
               job.save()
               #get the list of orgs to request from the form
               for org_id in request.POST.getlist('organization'):
                   organization = Organization.objects.get(id = org_id)
                   jr = JobRequest.objects.create(organization=organization, job = job)
                   link = request.build_absolute_uri(reverse('jobrequest_dash', kwargs = {'job_id': jr.job.id, 'organization_id': org_id}))
                   send_mail('BoilerConnect - New Job submitted', 'There is a job created for your organization. Click on the link to see the request. {0}'.format(link),'boilerconnect1@gmail.com', [organization.email], fail_silently=False)
                   for user in organization.group.user_set.all():
                       notify.send(request.user, recipient = user, verb = 'sent {0} a job request'.format(organization.name))
               message = "Job {0} created".format( job.name )
               return render(request,'dbtest/confirm.html', {'confirm':message})
           else:
               return render(request, 'dbtest/job_creation.html', {'form':form,'error':"There are incorrect fields"})
       #if the request was a GET
       else:
           orgs = Organization.objects.all()
           form = JobCreateForm()
           return render(request, 'dbtest/job_creation.html', {'form':form, 'orgs':orgs})

def about(request):
    return render(request, 'dbtest/about.html')
