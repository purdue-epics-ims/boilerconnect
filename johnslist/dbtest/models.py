from django.db import models
from django.forms import ModelForm,PasswordInput
from django.contrib.auth import forms
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User,Group
from guardian.shortcuts import assign_perm

class UserProfile(models.Model):
    def __unicode__(self):
        return self.name

    name = models.TextField('Username')
    user = models.OneToOneField(User) # UserProfile - User
    # purdueuser or communitypartner
    purdueuser = models.BooleanField(default=True)

class Category(models.Model):
    def __unicode__(self):
        return self.name

    name = models.CharField('Service Category Name',max_length=64)
    description = models.TextField('Service Category Description')

class Organization(models.Model):
    def __unicode__(self):
        return self.name

    name = models.TextField('Organization Name',null=True)
    description = models.TextField('Organization Description')
    categories = models.ManyToManyField(Category)  # Category =-= Organization
    email = models.CharField('Organization email',max_length=64,null=True)
    group = models.OneToOneField(Group) # Organization - Group
    phone_number = models.CharField('Organization phone number',max_length=64,null=True)
    icon = models.ImageField(upload_to='organization',null=True, blank=True)
    available = models.BooleanField(default=True)

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
    description = models.TextField('Job Description')
    duedate = models.DateTimeField('Date Due')
    creator = models.ForeignKey(User,related_name = 'jobs')  # User -o= Job
    organization = models.ManyToManyField(Organization, through = 'JobRequest')
    categories = models.ManyToManyField(Category)

    class Meta:
        permissions = (
            ( 'view_job','Can view Job' ),
            ( 'edit_job','Can edit Job'),
            ( 'is_creator', 'Is a creator of Job')
            )

    # function returns an array list of organization objects that have accepted = True in Jobrequest
    def jobrequests_accepted(self):
        accepted = JobRequest.objects.filter(job = self, accepted = True)
        return accepted
    def jobrequests_pending(self):
        pending = JobRequest.objects.filter(job = self, accepted = False, declined = False, completed = False)
        return pending
    def jobrequests_declined(self):
        declined = JobRequest.objects.filter(job = self, declined = True)
        return declined
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
    job = models.ForeignKey(Job,related_name = 'jobrequests') # Job -= JobRequest
    organization = models.ForeignKey(Organization)
    accepted = models.NullBooleanField(default = False)	
    declined = models.NullBooleanField(default = False)
    completed = models.NullBooleanField(default = False)

    class Meta:
            permissions = (
                ( 'view_jobrequest','Can view JobRequest' ),
                ( 'edit_jobrequest','Can edit JobRequest'),
                )

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

class Comment(models.Model):
    text_comment = models.TextField('text_comment')
    jobrequest = models.ForeignKey(JobRequest)
