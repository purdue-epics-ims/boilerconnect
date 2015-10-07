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
            [x] - user_create
            [] - user_edit
            [] - user_job_index
            [] - user_membership
            [] - permissions on views (user,job, org)

    Job:
        Backend:
            [x] - default permissions (creator has perms, accepted/requested have perms)
            [x] - setUpJobrelation (check requested/accepted relation exists)
            [x] - organization_accepted (use setUpJobrelation)
            [x] - organization_requested (use setUpJobrelation)
        Interface:
            [x] - job_create (check job exists, check default perms, check requested orgs)
            [x] - job_detail (check r.context['job'] is the same that was created)

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

#generic setup for all testcases
def set_up(self):
        #create user
        self.u = User.objects.create(username='foobar_user')
        self.u.set_password('asdf')
        self.u.save()
        #create group/org
        self.g=Group.objects.create(name="foobar_group")
        self.o = Organization.objects.create(name = self.g.name, group = self.g, description="test description",email="test@email.com",phone_number="123-456-7890")
        self.o.icon.save('plug.png', File(open(PIC_POPULATE_DIR+'plug.png')), 'r')
        #create category owned by foobar_user
        self.cat = Category.objects.create(name='foobar_category',description="test description")
        self.j = Job.objects.create(name='foobar_job',description="test description",duedate='2015-01-01',creator=self.u)



class UserTestCase(TestCase):
    #django calls this initialization function automatically
    def setUp(self):
        set_up(self)
        self.u2 = User.objects.create(username='foobar_user1')
        self.u2.set_password('asdf')
        self.u2.save()

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
        #successful user creation
        response = self.client.post(reverse('user_create'), {'username': 'user', 'password1':'zxcv', 'password2':'zxcv'})
        self.assertTrue('Thank you for creating an account' in response.content)
        
        #unsuccessful user creation
        response = self.client.post(reverse('user_create'), {'username': 'user1', 'password1':'zxcv', 'password2':'zxcvhg'})
        self.assertFalse('Thank you for creating an account' in response.content)

    def test_user_edit(self):
        response = self.client.post(reverse('user_edit'))
        self.assertTrue(response.status_code == 302)
        login_as(self, self.u.username, 'asdf')
        response = self.client.post(reverse('user_edit'))
        self.assertTrue(response.status_code == 200)

        pass
    def test_user_job_index(self):
        pass
    def test_user_membership(self):
        pass
    def test_view_permissions(self):
        r = login_as(self,self.u.username,'asdf')
        #verify user can view their own detail page
        response = self.client.get(reverse('user_detail',kwargs={'user_id':format(self.u.id)}))
        self.assertFalse('error' in r.context)
        self.assertTrue(response.status_code == 200)
        #verify user cannot access other users detail page
        response = self.client.get(reverse('user_detail',kwargs={'user_id':format(self.u2.id)}))
        self.assertTrue('error' in r.context)

class JobTestCase(TestCase):
    #django calls this initialization function automatically
    def setUp(self):
        set_up(self)
        self.j2 = Job.objects.create(name='test_job',description="test description",duedate='2015-01-01',creator=self.u)

    ### Backend Tests ###

    #ensure job is editable by creator 
    def test_permissions(self):
        self.assertTrue(self.u.has_perm('edit_job',self.j))
        self.assertTrue(self.u.has_perm('view_job',self.j))

    #check job relation function
    def test_setUpJobrelation(self):
        jr = self.j.setUpJobrelation(self.o,False)
        self.assertIsInstance(jr,Jobrelation)

    #check organizations that have accepted this job
    def test_organization_accepted(self):
        jr = self.j.setUpJobrelation(self.o,False)
        self.assertEqual(0,len(self.j.organization_accepted()))
        jr.accepted = True
        jr.save()
        self.assertEqual(1,len(self.j.organization_accepted()))
        self.assertTrue(self.o in self.j.organization_accepted())

    #check organizations where this job is requested
    def test_organization_requested(self):
        self.assertEqual(0,len(self.j.organization_requested()))
        jr = self.j.setUpJobrelation(self.o,False)
        self.assertEqual(1,len(self.j.organization_requested()))
        self.assertTrue(self.o in self.j.organization_requested())

    ### Interface Tests ###

    def test_job_create(self):
        #Login
        login_as(self,self.u.username,'asdf')
        #check logged in as user0
        r = self.client.get(reverse('front_page'))
        self.assertEqual(r.context['user'],self.u)

        #Create a job
        r = self.client.post(reverse('job_create'),{'name':'interfacejob','description':"testjob description",'duedate':'2015-09-05','organization':self.o.pk,'categories':self.cat.pk},follow=True)
        self.assertEqual(r.status_code, 200)

        #check if job exists
        self.assertTrue(Job.objects.filter(name='interfacejob').first())

    def test_job_detail(self):
        login_as(self,self.u.username,'asdf')
        r = self.client.get(reverse('job_detail',kwargs={'job_id':self.j2.id}))
        self.assertEqual(self.j2,r.context['job'])


class OrganizationTestCase(TestCase):
    #django calls this initialization function automatically
    def setUp(self):
        set_up(self)

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
