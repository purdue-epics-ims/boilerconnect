from django.db import models

# Create your models here.
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
	categories = models.ManyToManyField(ServiceCategory)  # ServiceCategory =-= Organization

class Job(models.Model):
	def __unicode__(self):
		return self.name

	name = models.CharField('Job Name',max_length=128)
	description = models.TextField('Job Description')
	accepted = models.BooleanField('Job Accepted?')
	duedate = models.DateTimeField('Date Due')
	creator = models.ForeignKey(User)  # User -o= Job
	requested = models.ManyToManyField(Organization,related_name='requested')  # Organization =-= Job
	accepted = models.ManyToManyField(Organization,related_name='accepted')  # Organization =-= Job

