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

	name = models.CharField('Category Name',max_length=64)
	description = models.TextField('Category Description')

class Organization(models.Model):
    def __unicode__(self):
        return self.name

    name = models.CharField('Organization Name',max_length=64,unique=True)
    description = models.TextField('Organization Description')
    group = models.OneToOneField(Group,related_name='group')
    categories = models.ManyToManyField(Category)  # Category =-= Organization
    email = models.CharField('Organization email',max_length=64,null=True)
    phone_number = models.CharField('Organization phone number',max_length=64,null=True)
    icon = models.ImageField(upload_to='organization',null=True)

    def get_admins(self):
        return [user for user in self.group.user_set.all() if user.has_perm('is_admin',self)]

    class Meta:
        permissions = (
            ( 'view_organization','Can view Organization' ),
            ( 'is_admin', 'Is an Administrator'),
            )

@receiver(post_save, sender=Organization)
def add_perms_organization(sender,**kwargs):
    #check if this post_save signal was generated from a Model create
    if 'created' in kwargs and kwargs['created']:
        organization=kwargs['instance']

        # allow organization to view itself by default
        assign_perm('view_organization',organization.group,organization)

class Job(models.Model):
	def __unicode__(self):
		return self.name

	name = models.CharField('Job Name',max_length=128)
	description = models.TextField('Job Description')
	duedate = models.DateTimeField('Date Due')
	creator = models.ForeignKey(User,related_name = 'creator')  # User -o= Job
	requested = models.ManyToManyField(Organization,related_name='requested')  # Organization =-= Job
	accepted = models.ManyToManyField(Organization,related_name='accepted') 
	categories = models.ManyToManyField(Category)

