from django.db import models
from django.forms import ModelForm,PasswordInput
from django.contrib.auth.models import User
from django.contrib.auth import forms

'''
Represented here are the minimum viable product entities for the BoilerConnect website.
The ManyToMany and ForeignKey fields represent relationships between 2 classes.  For example, the 'ForeignKey' field in
class Organization means that there is 1 admin associated with each Organization, and that it is a required relation for an Organization
to exist (since it is defined as an attribute in the Organization class).  Conversely, a user does not have any relationships defined in its class,
so Users can exist without be tied to any Organization.

The 'related_name' argument that appears in the Organization class renames the relationship.  Django names relationships based on what classes are being linked,
so if we didn't have 'related_name', the 'admin' and 'members' relationship in Organization would have the same name in our SQL database.


Future entities to add:
	- user hierarchy -> admin, member
	- reviews
	- media (pictures attached to posts, etc.)
'''

''' User class
	attributes:
		username
		password
'''

class ServiceCategory(models.Model):
	def __unicode__(self):
		return self.name

	name = models.CharField('Service Category Name',max_length=64)
	description = models.TextField('Service Category Description')

class Organization(models.Model):
	def __unicode__(self):
		return self.name
	
	def job_accepted(self):
		job_list_a = Job.objects.filter(jobrelation__organization = self,jobrelation__accepted = True)	
		return job_list_a

	def job_requested(self):
		job_list_r = Job.objects.filter(jobrelation__organization = org,jobrelation__accepted = False)
		return job_list_r

	name = models.CharField('Organization Name',max_length=64,unique=True)
	description = models.TextField('Organization Description')
	admin = models.ForeignKey(User,related_name='admin')  # User -o= Organization 
	members = models.ManyToManyField(User,related_name='members')  # User =-= Organization
	categories = models.ManyToManyField(ServiceCategory)  # ServiceCategory =-= Organization
	email = models.CharField('Organization email',max_length=64,null=True)  #should this be unique?
	phone_number = models.CharField('Organization phone number',max_length=64,null=True) #should this be unique?
	icon = models.ImageField(upload_to='organization',null=True)

class Job(models.Model):
	def __unicode__(self):
		return self.name
	# function returns an array list of organization objects that have accepted = True in JobRelation
	def organization_accepted(self):
		accepted = Organization.objects.filter(jobrelation__job = self,jobrelation__accepted = True)
		return accepted
	def organization_requested(self):
		requested = Organization.objects.filter(jobrelation__job = self,jobrelation__accepted = False)
		return requested

	name = models.CharField('Job Name',max_length=128)
	description = models.TextField('Job Description')
	duedate = models.DateTimeField('Date Due')
	creator = models.ForeignKey(User,related_name = 'creator')  # User -o= Job
	organization = models.ManyToManyField(Organization, through = 'JobRelation')
	categories = models.ManyToManyField(ServiceCategory)

class Jobrelation(models.Model):
	job = models.ForeignKey(Job)
	organization = models.ForeignKey(Organization)
	accepted = models.NullBooleanField(default = False)

	
