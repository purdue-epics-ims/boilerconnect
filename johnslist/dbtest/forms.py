from django.db import models
from django.forms import ModelForm,PasswordInput,Textarea, RadioSelect
from django.contrib.auth.models import User
from django.contrib.auth import forms
from .models import*
from django.core.mail import send_mail

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

        #make a request to all the new organizations
        for org in self.cleaned_data['organization']:
            if org not in job.organization.all():
                verb = "submitted"
                organization = Organization.objects.get(id = org.pk)
                jr = JobRequest.objects.create(organization=organization, job = job)
                link = request.build_absolute_uri(reverse('jobrequest_dash', kwargs = {'job_id': jr.job.id, 'organization_id': org.pk}))
                for user in organization.group.user_set.all():
                    send_mail('BoilerConnect - New Job submitted', 'There is a job created for your organization. Click on the link to see the request. {0}'.format(link),'boilerconnect1@gmail.com', [user.userprofile.email], fail_silently=False)

        #delete request for all organizations removed
        for org in job.organization.all():
            if org not in self.cleaned_data['organization']:
                organization = Organization.objects.get(id = org.pk)
                jr =  JobRequest.objects.get(organization=organization, job = job).delete()

        return job

class JobCreateForm(JobForm):
    class Meta:
        model = Job
        exclude = ('creator',)

class JobEditForm(JobForm):
    class Meta:
        model = Job
        exclude = ('creator',)

class CommentCreateForm(ModelForm):
    class Meta:
        model = Comment
        exclude = ('jobrequest',)

class ProfileCreationForm(ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user','visited_views')
