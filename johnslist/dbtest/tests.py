from dbtest.models import *
from django.test import TestCase
from django.core.files import File
from django.core.urlresolvers import reverse
#for login test
from django.contrib.auth.models import AnonymousUser

from django.test import Client

'''
    todo:  [] - group tests by model they test

    User:
    Interface:
        [] - login
        [] - user_create
        [] - user_edit
        [] - user_job_index
        [] - user_membership
        [] - permissions on views (user,job, org)

    Job:
        Backend:
            [] - default permissions (creator has perms, accepted/requested have perms)
            [] - setUpJobrelation (check requested/accepted relation exists)
            [] - organization_accepted (use setUpJobrelation)
            [] - organization_requested (use setUpJobrelation)
        Interface:
            [] - job_create (check job exists, check default perms, check requested orgs)
            [] - job_detail (check r.context['job'] is the same that was created)

    Organization:
        Backend:
            [] - default permissions (admin has perms, members have perms)
            [] - jobs_requested
            [] - jobs_accepted
            [] - get_admins
        Interface:
            [] - org_detail
            [] - org accept/decline jobs
            [] - organization create
            [] - organization edit
'''

#Test object creation and default perms
class ObjectCreateTestCase(TestCase):
    fixtures = ['unittest.json']
    def setUp(self):
        self.g = Group.objects.get(name="Purdue Linux Users Group")
        self.o = self.g.organization

        self.u = User.objects.get(username='user0')

        self.j = Job.objects.get(name='Installing linux')

        self.cat = Category.objects.get(name='computer science')

    def test_organization_create(self):
        #check permissions

    def test_job_create(self):
        #check permissions

#Test views involved in the creation of objects
class InterfaceCreateTestCase(TestCase):
    fixtures = ['unittest.json']
    def setUp(self):
        self.g = Group.objects.get(name="Purdue Linux Users Group")
        self.o = self.g.organization

        self.u = User.objects.get(username='user0')

        self.j = Job.objects.get(name='Installing linux')

        self.cat = Category.objects.get(name='computer science')

    #Test job create through interface
    def test_job_create(self):
        #Login
        r = self.client.post(reverse("login"),{'username':'user0','password':'asdf'},follow=True)
        self.assertEqual(r.status_code, 200)

        #Create a job
        r = self.client.post(reverse('job_create'),{'name':'interfacejob','description':'testjob description','duedate':'2015-09-05','organization':self.o.pk,'categories':self.cat.pk},follow=True)
        self.assertEqual(r.status_code, 200)
        #check if job exists
        self.assertTrue(Job.objects.filter(name='interfacejob').first())


#Test views which don't create objects
class ViewsTestCase(TestCase):
    fixtures = ['unittest.json']
    def setUp(self):
        self.g = Group.objects.get(name="Purdue Linux Users Group")
        self.o = self.g.organization

        self.u = User.objects.get(username='user0')

        self.j = Job.objects.get(name='Installing linux')

        self.cat = Category.objects.get(name='computer science')
        self.g = Group.objects.create(name="Testorg")

    #Test user login/logout
    def test_login(self):
        #Test for login failure
        r = self.client.post(reverse('login'),{'username':'fake_user','password':'no_password'})
        self.assertEqual(r.status_code, 200)
        self.assertTrue('error' in r.context)

        #Test successful login
        r = self.client.post(reverse('login'),{'username':self.u.username,'password':'asdf'})
        #check redirect
        self.assertRedirects(r,reverse('front_page'))
        #check logged in as user0
        r = self.client.get(reverse('front_page'))
        self.assertEqual(r.context['user'],self.u)

        #Test logout
        r = self.client.get(reverse('logout'))
        self.assertEqual(type(r.context['user']),AnonymousUser)
