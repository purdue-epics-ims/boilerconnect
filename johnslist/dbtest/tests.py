from dbtest.models import *
from django.test import TestCase
from django.core.files import File
from johnslist.settings import PIC_POPULATE_DIR

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
