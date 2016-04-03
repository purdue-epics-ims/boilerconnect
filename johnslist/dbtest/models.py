from django.db import models
from django.forms import ModelForm,PasswordInput
from django.contrib.auth import forms
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User,Group
from guardian.shortcuts import assign_perm, remove_perm
from notifications.signals import notify
from django.core.urlresolvers import reverse

class UserProfile(models.Model):
    def __unicode__(self):
        return self.user.username

    user = models.OneToOneField(User,related_name = 'userprofile',null=True, blank = False) # UserProfile - User
    # purdueuser or communitypartner
    purdueuser = models.BooleanField(default=True, choices=((True, 'Purdue User'),(False, 'Community User')))
    # save which pages the user has visited before for the purposes of showing helpful dialogs
    visited_views = models.CharField(max_length=64,default="")

class Category(models.Model):
    def __unicode__(self):
        return self.name

    name = models.CharField('Service Category Name',max_length=64)
    description = models.TextField('Service Category Description')

class Organization(models.Model):
    def __unicode__(self):
        return self.name

    name = models.CharField('Organization Name',max_length=64)
    description = models.TextField('Organization Description')
    categories = models.ManyToManyField(Category)  # Category =-= Organization
    email = models.CharField('Organization email',max_length=64)
    group = models.OneToOneField(Group) # Organization - Group
    phone_number = models.CharField('Organization phone number',max_length=64)
    icon = models.ImageField(upload_to='organization', null=True)
    available = models.BooleanField(default=True,choices=((True, "Accepting Jobs"),(False, "Not accepting Jobs")))

    class Meta:
		permissions = (
            ( 'view_organization','Can view Organization' ),
            ( 'edit_organization','Can edit Organization' ),
            ( 'is_admin', 'Is an Administrator')
            )

    #get list of jobs accepted for Org
    def jobrequests_accepted(self):
        return JobRequest.objects.filter(organization = self,accepted = True,completed = False)

    #get list of jobs pending for Org
    def jobrequests_pending(self):
        return JobRequest.objects.filter(organization = self,accepted = False,declined = False)

    #get list of jobs declined by Org
    def jobrequests_declined(self):
        return JobRequest.objects.filter(organization = self,accepted = False,declined = True)

    #get list of jobs completed by Org
    def jobrequests_completed(self):
        return JobRequest.objects.filter(organization = self,completed = True)

    #get admins of this org
    def get_admins(self):
		return [user for user in self.group.user_set.all() if user.has_perm('is_admin',self)]


@receiver(post_save, sender=Organization)
def add_perms_organization(sender,**kwargs):
    #check if this post_save signal was generated from a Model create (vs a Model edit)
    if 'created' in kwargs and kwargs['created']:
        organization=kwargs['instance']

        # allow organization to view and edit itself by default
        assign_perm('view_organization',organization.group,organization)
        assign_perm('edit_organization',organization.group,organization)

class Job(models.Model):
    def __unicode__(self):
        return self.name
    name = models.CharField('Job Name',max_length=128)
    client_organization = models.CharField('What organization do you represent?', max_length=64) #what entity/organization needs this job?
    description = models.TextField('Job Description', max_length=256) #short description
    deliverable = models.TextField('Deliverable', max_length=256) #end product to be delivered
    duedate = models.DateTimeField('Date Due') #when Job is due for completion
    stakeholders = models.TextField('Stakeholders') #all persons who may be affected by project
    tech_specs = models.TextField('Technical Specifications', blank = True) #important technical requirements
    budget = models.CharField('Budget', max_length=64) #budget estimate
    attachments = models.FileField(upload_to='job', blank = True) #file attachments
    creator = models.ForeignKey(User,related_name = 'jobs')  # User -o= Job
    organization = models.ManyToManyField(Organization, through = 'JobRequest')
    closed = models.NullBooleanField(default = False)

    class Meta:
        permissions = (
            ( 'view_job','Can view Job' ),
            ( 'edit_job','Can edit Job'),
            ( 'is_creator', 'Is a creator of Job')
            )

    # returns JobRequests that have been accepted
    def jobrequests_accepted(self):
        accepted = JobRequest.objects.filter(job = self, accepted = True)
        return accepted
    # returns JobRequests that are pending
    def jobrequests_pending(self):
        pending = JobRequest.objects.filter(job = self, accepted = False, declined = False, completed = False)
        return pending
    # returns JobRequests that have been declined
    def jobrequests_declined(self):
        declined = JobRequest.objects.filter(job = self, declined = True)
        return declined
    # creates a new JobRequest
    def request_organization(self,organization):
        jr = JobRequest.objects.create(job = self,organization = organization);
        return jr

#add default job permissions
@receiver(post_save, sender=Job)
def add_perms_job(sender,**kwargs):
    #check if this post_save signal was generated from a Model create
    if 'created' in kwargs and kwargs['created']:
        job=kwargs['instance']

        #allow creator to view and edit job
        assign_perm('view_job',job.creator,job)
        assign_perm('edit_job',job.creator,job)
        #allow requested orgs to view job
        for org in job.organization.all():
            assign_perm('view_job',org.group,job)

class JobRequest(models.Model):
    def __unicode__(self):
        return self.job.name

    job = models.ForeignKey(Job,related_name = 'jobrequests') # Job -= JobRequest
    organization = models.ForeignKey(Organization)
    accepted = models.NullBooleanField(default = False)	
    declined = models.NullBooleanField(default = False)
    confirmed = models.NullBooleanField(default = False)
    completed = models.NullBooleanField(default = False)

    class Meta:
            permissions = (
                ( 'view_jobrequest','Can view JobRequest' ),
                ( 'edit_jobrequest','Can edit JobRequest'),
                ( 'edit_jobrequest_state','Can edit JobRequest state'),
                )

    # set a JobRequest as accepted
    def accept(self):
        self.accepted = True
        self.declined = False
        self.save()
        notify.send(self.organization,
                    verb="accepted",
                    action_object=self.job,
                    recipient=self.job.creator,
                    url=reverse('jobrequest_dash',
                                kwargs={'organization_id':self.organization.id,'job_id':self.job.id}) )

    # set a JobRequest as pending
    def pend(self):
        self.accepted = False
        self.declined = False
        self.save()
        notify.send(self.organization,
                    verb="accepted",
                    action_object=self.job,
                    recipient=self.job.creator,
                    url=reverse('jobrequest_dash',
                                kwargs={'organization_id':self.organization.id,'job_id':self.job.id}) )

    # set a JobRequest as declined
    def decline(self):
        self.declined = True
        self.accepted = False
        self.save()
        notify.send(self.organization,
                    verb="declined",
                    action_object=self.job,
                    recipient=self.job.creator,
                    url=reverse('jobrequest_dash',
                                kwargs={'organization_id':self.organization.id,'job_id':self.job.id}) )

    #set a JobRequest as confirmed
    def confirm(self):
        self.declined = False
        self.accepted = True
        self.confirmed = True
        self.save()
        notify.send(self.organization,
                    verb="confirmed",
                    action_object=self.job,
                    recipient=self.organization.group,
                    url=reverse('jobrequest_dash',
                                kwargs={'organization_id':self.organization.id,'job_id':self.job.id}) )
        # iterate through all jobrequests in this job and remove permission for other jobrequests 
        job = self.job
        job.closed = True
        job.save()
        for jr in job.jobrequests.all():
            if jr != self:
                remove_perm('view_jobrequest',jr.job.creator,jr)
                remove_perm('view_jobrequest',jr.organization.group,jr)
                notify.send(self.organization,
                        verb="has closed the job: ",
                            action_object=self.job,
                            recipient=jr.organization.group,
                            url=reverse('jobrequest_dash',
                                        kwargs={'organization_id':jr.organization.id,'job_id':jr.job.id}) )
        


   #check if a jobrequest is pending 
    def is_pending(self):
        if not self.accepted and not self.declined:
            return True
        else:
            return False
        
#add default jobrequest permissions
@receiver(post_save, sender=JobRequest)
def add_perms_jobrequest(sender,**kwargs):
    #check if this post_save signal was generated from a Model create
    if 'created' in kwargs and kwargs['created']:
        jobrequest=kwargs['instance']
        job = jobrequest.job

        #allow creator to view and edit jobrequest
        assign_perm('view_jobrequest',job.creator,jobrequest)
        assign_perm('edit_jobrequest',job.creator,jobrequest)
        #allow requested org to view jobrequest
        assign_perm('view_jobrequest',jobrequest.organization.group,jobrequest)
        #allow Purdue user to edit jobrequest state
        assign_perm('edit_jobrequest_state',jobrequest.organization.group,jobrequest)

        #notify users of new JobRequest
        notify.send(job.creator,
                    verb="submitted",
                    action_object=jobrequest,
                    recipient=jobrequest.organization.group,
                    url=reverse('jobrequest_dash',
                                kwargs={'organization_id':jobrequest.organization.id,'job_id':job.id}) )
    else:
        #notify users of changed JobRequest
        notify.send(job.creator,
                    verb="modified",
                    action_object=jobrequest,
                    recipient=jobrequest.organization.group,
                    url=reverse('jobrequest_dash',
                                kwargs={'organization_id':jobrequest.organization.id,'job_id':job.id}) )

class Comment(models.Model):
    text_comment = models.TextField('text_comment')
    jobrequest = models.ForeignKey(JobRequest)
    creator = models.ForeignKey(User, blank = True, null = True) #creator added after form is validated
