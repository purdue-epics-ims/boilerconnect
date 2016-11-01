from django.db import models
from django.forms import ModelForm, CheckboxSelectMultiple
from django.contrib.auth.models import User
from django.contrib.auth import forms
from .models import*
from django.core.mail import send_mail
from .widgets import *

class OrganizationCreateForm(ModelForm):
    class Meta:
		model = Organization
		fields = ['name','description','categories','icon']

class OrganizationEditForm(ModelForm):

	class Meta:
		model = Organization
		fields = ['name','description','categories','icon','available']

class JobForm(ModelForm):
    def save(self, request, commit = True):
        job = super(JobForm, self).save(commit = False)
        job.creator = request.user
        job.save()

        # normally you would have save_m2m(), but the fact that `organizations` is a relation
        # through a model prevents this

        # need to save category relations here

        # make a request to all the new organizations
        for org in self.cleaned_data['organizations']:
            if org not in job.organizations.all():
                verb = "submitted"
                organization = Organization.objects.get(id = org.pk)
                jr = JobRequest.objects.create(organization=organization, job = job)
                link = request.build_absolute_uri(reverse('organization_dash', kwargs = {'organization_id': org.pk})+"?jobrequestID="+str(jr.id))
                for user in organization.group.user_set.all():
                    send_mail('BoilerConnect - New Job submitted', 'There is a job created for your organization. Click on the link to see the request. {0}'.format(link),'boilerconnect1@gmail.com', [user.userprofile.email], fail_silently=False)

        # do we want the user to be able to delete requests or categories?
        # # remove deleted categories
        # for cat in job.categories.all():
        #     if cat not in self.cleaned_data['categories']:
        #         job.categories.remove(cat)

        # # delete request for all organizations removed
        # for org in job.organizations.all():
        #     if org not in self.cleaned_data['organizations']:
        #         organization = Organization.objects.get(id = org.pk)
        #         jr =  JobRequest.objects.get(organization=organization, job = job).delete()

        return job

class JobCreateForm(JobForm):
    class Meta:
        model = Job
        exclude = ('creator',)
        widgets = { 'organizations': OrgSelect(),
                    'categories': CategorySelect()}

class JobEditForm(JobForm):
    class Meta:
        model = Job
        exclude = ('creator',)
        widgets = { 'organizations': OrgSelect(),
                    'categories': CategorySelect()}

class CommentCreateForm(ModelForm):
    class Meta:
        model = Comment
        exclude = ('jobrequest',)

class ProfileCreationForm(ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user','visited_views')
