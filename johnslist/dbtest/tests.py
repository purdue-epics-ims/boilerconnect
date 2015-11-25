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
            [x] - user_edit
            [x] - user_job_index
            [] - permissions on views (user,job, org)

    Job:
        Backend:
            [x] - default permissions (creator has perms, accepted/pending have perms)
            [x] - request_organization (check requested/accepted relation exists)
            [x] - jobrequests_accepted (use request_organization)
            [x] - jobrequests_pending (use request_organization)
            [x] - jobrequests_declined (use request_organization)
        Interface:
            [x] - job_create (check job exists, check default perms, check requested orgs)
            [x] - jobrequest_dash (check r.context['job'] is the same that was created)

    Organization:
        Backend:
            [x] - default permissions (admin has perms, members have perms)
            [x] - jobs_accepted
            [x] - jobs_pending
            [x] - jobs_declined
            [x] - jobs_completed
            [x] - get_admins
        Interface:
            [x] - org_detail
            [] - org accept/decline jobs
            [x] - organization create
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
        UserProfile.objects.create(name = self.u.username, user = self.u, purdueuser = True)
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
        response = self.client.post(reverse('user_create'), {'username': 'user', 'password1':'zxcv', 'password2':'zxcv', 'user_type': 'purdue'})
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
        #change the users username, then try to log in again

    def test_view_permissions(self):
        #verify user is redirected
        r = self.client.get(reverse('user_dash'))
        self.assertRedirects(r,'/login?next='+reverse('user_dash'))
        login_as(self,self.u.username,'asdf')
        #verify user can view their own detail page
        r = self.client.get(reverse('user_dash',))
        self.assertFalse('error' in r.context)
        self.assertTrue(r.status_code == 200)

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

    #check creating a jobrequest
    def test_request_organization(self):
        jr = self.j.request_organization(self.o)
        self.assertIsInstance(jr,JobRequest)

    #check if accepted job requets are returned
    def test_jobrequests_accepted(self):
        jr = self.j.request_organization(self.o)
        self.assertEqual(0,len(self.j.jobrequests_accepted()))
        jr.accepted = True
        jr.save()
        self.assertEqual(1,len(self.j.jobrequests_accepted()))
        self.assertTrue(jr in self.j.jobrequests_accepted())

    #check if pending jobreuqests are returned
    def test_jobrequests_pending(self):
        self.assertEqual(0,len(self.j.jobrequests_pending()))
        jr = self.j.request_organization(self.o)
        self.assertEqual(1,len(self.j.jobrequests_pending()))
        self.assertTrue(jr in self.j.jobrequests_pending())

    #rcheck if declined jobrequests are returned
    def test_jobrequests_declined(self):
        jr = self.j.request_organization(self.o)
        self.assertFalse(jr in self.j.jobrequests_declined())
        jr.declined = True
        jr.save()
        self.assertTrue(jr in self.j.jobrequests_declined())

    ### Interface Tests ###

    #verify job_create view
    def test_job_create(self):
        #Login
        self.u.userprofile.purdueuser = False
        login_as(self,self.u.username,'asdf')
        #check logged in as user0
        r = self.client.get(reverse('front_page'))
        self.assertEqual(r.context['user'],self.u)

        #Create a job
        r = self.client.post(reverse('job_create'),{'name':'interfacejob','description':"testjob description",'duedate':'2015-09-05','organization':self.o.pk,'categories':self.cat.pk},follow=True)
        self.assertEqual(r.status_code, 200)

        #check if job exists
#self.assertTrue(Job.objects.filter(name='interfacejob').first())

    #verify jobrequest_dash view
    def test_jobrequest_dash(self):
        login_as(self,self.u.username,'asdf')
        jr = self.j2.request_organization(self.o)
        r = self.client.get(reverse('jobrequest_dash',kwargs={'job_id':self.j2.id,'organization_id':self.o.id}))
        self.assertEqual(jr,r.context['jobrequest'])


class OrganizationTestCase(TestCase):
    #django calls this initialization function automatically
    def setUp(self):
        set_up(self)
        #add foobar_user to org
        self.o.group.user_set.add(self.u)
        #nonmember_user is not a member
        self.u2 = User.objects.create(username='nonmember_user')
        self.u2.set_password('asdf')
        self.u2.save()
        UserProfile.objects.create(name = self.u2.username, user = self.u2, purdueuser = True)

    ### Backend Tests ###

    #check default permissions on newly created Organizations
    def test_permissions(self):
        self.assertTrue(self.u.has_perm('view_organization',self.o))
        self.assertTrue(self.u.has_perm('edit_organization',self.o))
        self.assertFalse(self.u2.has_perm('view_organization',self.o))
        self.assertFalse(self.u2.has_perm('edit_organization',self.o))

    #test Organization.jobs_pending
    def test_jobs_pending(self):
        self.j.request_organization(self.o)
        jr = self.j.request_organization(self.o)
        self.assertTrue(jr in self.o.jobrequests_pending())

    #test Organization.jobs_declined
    def test_jobs_declined(self):
        jr = self.j.request_organization(self.o)
        jr.declined = True
        jr.save()
        self.assertTrue(jr in self.o.jobrequests_declined())

    #test Organization.jobs_completed
    def test_jobs_completed(self):
        jr = self.j.request_organization(self.o)
        self.assertTrue(jr in self.o.jobrequests_pending())
        jr.completed = True
        jr.save()
        self.assertTrue(jr in self.o.jobrequests_completed())

    #test Organization.get_admins
    def test_get_admins(self):
        self.o.group.user_set.add(self.u)
        assign_perm('is_admin',self.u,self.o)
        self.assertTrue(self.u in self.o.get_admins())
        

    ### Interface Tests ###

    #test organization_detail.html
    def test_org_detail(self):
        response = self.client.post(reverse('organization_detail', kwargs = {'organization_id': self.o.id}))
        self.assertTrue(response.status_code == 200)
        self.assertEqual(self.o, response.context['organization'])

    #test organization_accept.html
    def test_organization_accept_decline(self):
        self.o.group.user_set.add(self.u2) 
        login_as(self, self.u2.username, 'asdf')
        j1 = Job.objects.create(name='foobar_job1',description="test description",duedate='2015-01-01',creator=self.u2)
        j2 = Job.objects.create(name='foobar_job2',description="test description",duedate='2015-01-01',creator=self.u2)
        j1.request_organization(self.o)
        j2.request_organization(self.o)
        assign_perm('edit_organization', self.u2, self.o)

        #test accept job
        response = self.client.post(reverse('organization_accept_job', kwargs = {'organization_id': self.o.id}), {'job_id':j1.id, 'action':"Accept Job"})
        self.assertTrue(response.status_code == 200)
        #test decline job
        response = self.client.post(reverse('organization_accept_job', kwargs = {'organization_id': self.o.id}), {'job_id':j2.id, 'action':"Decline Job"})
        self.assertTrue(response.status_code == 200)

    #test org creation
    def test_organization_create(self):
        from johnslist.settings import PIC_POPULATE_DIR
        #when user is not logged in
        response = self.client.post(reverse('organization_create'))
        self.assertEqual(response.status_code, 302)
       
        #after login
        login_as(self, self.u2.username, 'asdf')
        category = self.cat.pk
        #creating the org
        with open(PIC_POPULATE_DIR+'plug.png') as icon:
            response = self.client.post(reverse('organization_create'), {'name': 'test org', 'description': 'testing org', 'categories': category, 'icon':icon})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(Organization.objects.get(name = 'test org'))
        org = Organization.objects.get(name = 'test org')
        response = self.client.get('/organization/{0}'.format(org.id))
        self.assertTrue(response.status_code == 200)

    #changing the organization attributes
    def test_organization_edit(self):
        self.o.group.user_set.add(self.u2) 
        login_as(self, self.u2.username, 'asdf')
        response = self.client.post(reverse('organization_edit', kwargs = {'organization_id': self.o.pk}))
        self.assertEqual(response.status_code, 200)


