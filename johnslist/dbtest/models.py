from django.db import models
from django.forms import ModelForm,PasswordInput
from django.contrib.auth import forms
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User,Group
from guardian.shortcuts import assign_perm

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
    
    def job_accepted(self):
        job_list_a = Job.objects.filter(jobrelation__organization = self,jobrelation__accepted = True,jobrelation__completed = False)    
        return job_list_a

    def job_requested(self):
        job_list_r = Job.objects.filter(jobrelation__organization = self,jobrelation__accepted = False,jobrelation__declined = False)
        return job_list_r
    def job_declined(self):
        job_list_d = Job.objects.filter(jobrelation__organization = self,jobrelation__accepted = False,jobrelation__declined = True)
        return job_list_d
	
    def job_completed(self):
        job_list_d = Job.objects.filter(jobrelation__organization = self, jobrelation__completed = True)
        return job_list_d

    def get_admins(self):
		return [user for user in self.group.user_set.all() if user.has_perm('is_admin',self)]

    class Meta:
		permissions = (
            ( 'view_organization','Can view Organization' ),
            ( 'edit_organization','Can edit Organization' ),
            ( 'is_admin', 'Is an Administrator')
            )

@receiver(post_save, sender=Organization)
def add_perms_organization(sender,**kwargs):
    #check if this post_save signal was generated from a Model create (vs a Model edit)
    if 'created' in kwargs and kwargs['created']:
        organization=kwargs['instance']

        # allow organization to view itself by default
        assign_perm('view_organization',organization.group,organization)

class Job(models.Model):
    def __unicode__(self):
        return self.name
    # function returns an array list of organization objects that have accepted = True in JobRelation
    def organization_accepted(self):
        accepted = Organization.objects.filter(jobrelation__job = self,jobrelation__accepted = True, jobrelation__completed = False)
        return accepted
    def organization_requested(self):
        requested = Organization.objects.filter(jobrelation__job = self,jobrelation__accepted = False,jobrelation__declined = False)
        return requested
    def organization_declined(self):
        declined = Organization.objects.filter(jobrelation__job = self,jobrelation__accepted = False,jobrelation__declined = True)
        return declined
    def setUpJobrelation(self,organization):
        jr = Jobrelation.objects.create(job = self,organization = organization);
        return jr

    name = models.CharField('Job Name',max_length=128)
    description = models.TextField('Job Description')
    duedate = models.DateTimeField('Date Due')
    creator = models.ForeignKey(User,related_name = 'creator')  # User -o= Job
    organization = models.ManyToManyField(Organization, through = 'Jobrelation')
    categories = models.ManyToManyField(Category)

    class Meta:
        permissions = (
            ( 'view_job','Can view Job' ),
            ( 'edit_job','Can edit Job'),
            ( 'is_creator', 'Is a creator of Job')
            )
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
        for org in job.organization_requested():
            assign_perm('view_job',org.group,job)

class Jobrelation(models.Model):
    job = models.ForeignKey(Job)
    organization = models.ForeignKey(Organization)
    accepted = models.NullBooleanField(default = False)	
    declined = models.NullBooleanField(default = False)
    completed = models.NullBooleanField(default = False)
