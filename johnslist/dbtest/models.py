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

	name = models.CharField('Job Name',max_length=128)
	description = models.TextField('Job Description')
	duedate = models.DateTimeField('Date Due')
	creator = models.ForeignKey(User,related_name = 'creator')  # User -o= Job
	requested = models.ManyToManyField(Organization,related_name='requested')  # Organization =-= Job
	accepted = models.ManyToManyField(Organization,related_name='accepted') 
	categories = models.ManyToManyField(ServiceCategory)

### Forms

class OrganizationCreateForm(ModelForm):
	class Meta:
		model = Organization
		fields = ['name','description','categories','icon']

class JobCreateForm(ModelForm):
	class Meta:
		model = Job
		fields = ['name','description','duedate','requested', 'categories']
