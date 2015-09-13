from dbtest.models import *
from django.test import TestCase
from django.core.files import File
from django.core.urlresolvers import reverse
from johnslist.settings import PIC_POPULATE_DIR
#for login test
from django.contrib.auth.models import AnonymousUser

from django.test import Client

'''
    todo:  [x] - group tests by model they test

    User:
        Interface:
            [x] - login
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



#login as user with provided password and return response
def login_as(self,user,password):
    return self.client.post(reverse("login"),{'username':user,'password':password},follow=True)



class UserTestCase(TestCase):
    def setUp(self):
        #create user
        self.u = User.objects.create(username='user0')
        self.u.set_password('asdf')
        self.u.save()

    ### Interface Tests ###

    def test_login(self):
        #Test for login failure
        r = login_as(self,'invalid_user0','password')
        self.assertEqual(r.status_code, 200)
        self.assertTrue('error' in r.context)

        #Test successful login
        r = self.client.post(reverse('login'),{'username':self.u.username,'password':'asdf'})
        r = login_as(self,self.u.username,'asdf')
        #check redirect
        self.assertRedirects(r,reverse('front_page'))
        #check logged in as user0
        r = self.client.get(reverse('front_page'))
        self.assertEqual(r.context['user'],self.u)

        #Test logout
        r = self.client.get(reverse('logout'))
        self.assertEqual(type(r.context['user']),AnonymousUser)

    def test_user_create(self):
        pass
    def test_user_edit(self):
        pass
    def test_user_job_index(self):
        pass
    def test_user_membership(self):
        pass
    def test_view_permissions(self):
        pass

class JobTestCase(TestCase):
    def setUp(self):
        #create user
        self.u = User.objects.create(username='user0')
        self.u.set_password('asdf')
        self.u.save()
        #create group/org
        self.g=Group.objects.create(name="test_group")
        self.o = Organization.objects.create(name = self.g.name, group = self.g, description="test description",email="test@email.com",phone_number="123-456-7890")
        self.o.icon.save('plug.png', File(open(PIC_POPULATE_DIR+'plug.png')), 'r')
        #create category
        self.cat = Category.objects.create(name='test_category',description="test description")

    ### Backend Tests ###

    #ensure job is editable by creator and viewable by associated orgs
    def test_permissions(self):
        #need to add permissions to Job model first
        pass

    #check job relation function
    def test_setUpJobrelation(self):
        pass

    #check organizations that have accepted this job
    def test_organization_accepted(self):
        pass

    #check organizations where this job is requested
    def test_organization_requested(self):
        pass

    ### Interface Tests ###

    def test_job_create(self):
        #Login
        login_as(self,'user0','asdf')
        #check logged in as user0
        r = self.client.get(reverse('front_page'))
        self.assertEqual(r.context['user'],self.u)

        #Create a job
        r = self.client.post(reverse('job_create'),{'name':'interfacejob','description':'testjob description','duedate':'2015-09-05','organization':self.o.pk,'categories':self.cat.pk},follow=True)
        self.assertEqual(r.status_code, 200)
        with open('/tmp/test','w') as f:
            f.write(r.content)

        #check if job exists
        self.assertTrue(Job.objects.filter(name='interfacejob').first())

    def test_job_detail(self):

        pass


class OrganizationTestCase(TestCase):

    ### Backend Tests ###

    def test_permissions(self):
        pass
    def test_jobs_requested(self):
        pass
    def test_get_admins(self):
        pass

    ### Interface Tests ###

    def test_org_detail(self):
        pass
    def test_organization_accept_decline(self):
        pass
    def test_organization_create(self):
        pass
    def test_organization_edit(self):
        pass
