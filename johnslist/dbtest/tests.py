from dbtest.models import *
from django.test import TestCase
from django.core.files import File
from django.core.urlresolvers import reverse
from johnslist.settings import PIC_POPULATE_DIR

from django.test import Client

class ObjectCreateTestCase(TestCase):
    def setUp(self):
        g = Group.objects.create(name="Testorg")
        plug = Organization.objects.create(
            name=g.name,
            group=g,
            description="test description",
            email="test_email@test.org",
            phone_number="123-456-7890")
        plug.icon.save('plug.png', File(open(PIC_POPULATE_DIR+'plug.png')), 'r')

        u = User.objects.create(username='user0')
        u.set_password('asdf')
        u.save()

        j = Job.objects.create(name='test job', description = 'Description of the job', duedate = '2015-3-21', creator = u)

    def test_object_create(self):
        group = Organization.objects.get(name='Testorg')
        self.assertIs(type(group), Organization)

class InterfaceCreateTestCase(TestCase):
    def setUp(self):
        self.g = Group.objects.create(name="Testorg")
        self.o = Organization.objects.create(
            name=self.g.name,
            group=self.g,
            description="test description",
            email="test_email@test.org",
            phone_number="123-456-7890")
        self.o.icon.save('plug.png', File(open(PIC_POPULATE_DIR+'plug.png')), 'r')

        self.u = User.objects.create(username='user0')
        self.u.set_password('asdf')
        self.u.save()

        self.j = Job.objects.create(name='test job', description = 'Description of the job', duedate = '2015-3-21', creator = self.u)

    #Test job create through interface
    def test_job_create(self):
        #Login
        r = self.client.post(reverse("login"),{'username':'user0','password':'asdf'},follow=True)
        self.assertEqual(r.status_code, 200)

        #Create a job
        r = self.client.post(reverse('job_create'),{'name':'interfacejob','description':'testjob description','duedate':'2015-09-05','creator':self.u.username,'organization':self.o.name},follow=True)
        self.assertEqual(r.status_code, 200)
        ### check if job exists


class ViewsTestCase(TestCase):
    def setUp(self):
        self.g = Group.objects.create(name="Testorg")
        self.o = Organization.objects.create(
            name=self.g.name,
            group=self.g,
            description="test description",
            email="test_email@test.org",
            phone_number="123-456-7890")
        self.o.icon.save('plug.png', File(open(PIC_POPULATE_DIR+'plug.png')), 'r')

        self.u = User.objects.create(username='user0')
        self.u.set_password('asdf')
        self.u.save()

        self.j = Job.objects.create(name='test job', description = 'Description of the job', duedate = '2015-3-21', creator = self.u)

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
        print '#########',r.context

        #Test logout
        r = self.client.get(reverse('logout'))
        print r.context


