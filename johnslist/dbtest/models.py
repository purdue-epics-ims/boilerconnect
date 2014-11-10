from django.db import models
from django.forms import ModelForm

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
class User(models.Model):
	def __unicode__(self):
		return self.name

	name = models.CharField('Username',max_length=64)
	password = models.CharField('Password',max_length=64)

class ServiceCategory(models.Model):
	def __unicode__(self):
		return self.name

	name = models.CharField('Service Category Name',max_length=64)
	description = models.TextField('Service Category Description')

class Organization(models.Model):
	def __unicode__(self):
		return self.name

	name = models.CharField('Organization Name',max_length=64)
	description = models.TextField('Organization Description')
	admin = models.ForeignKey(User,related_name='admin')  # User -o= Organization 
	members = models.ManyToManyField(User,related_name='members')  # User =-= Organization
	categories = models.ManyToManyField(ServiceCategory,related_name = 'categories')  # ServiceCategory =-= Organization

class Job(models.Model):
	def __unicode__(self):
		return self.name

	name = models.CharField('Job Name',max_length=128)
	description = models.TextField('Job Description')
	duedate = models.DateTimeField('Date Due')
	creator = models.ForeignKey(User,related_name = 'creator')  # User -o= Job
	requested = models.ManyToManyField(Organization,related_name='requested')  # Organization =-= Job
	accepted = models.ManyToManyField(Organization,related_name='accepted')  # Organization =-= Job

### Forms

class UserCreateForm(ModelForm):
	class Meta:
		model = User
		fields = ['name','password']

class OrganizationCreateForm(ModelForm):
	class Meta:
		model = Organization
		fields = ['name','description','categories']

class JobCreateForm(ModelForm):
	class Meta:
		model = Job
		fields = ['name','description','duedate','requested']
