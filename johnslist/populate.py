import os
from django.core.management import call_command
from itertools import cycle
from django.utils import timezone
import sys

def populate():
    print 'Populating database...'

    #--------------- Organizations ----------------
    print '  creating Organizations'

    #add Organizations
    g=Group.objects.create(name="Purdue Linux Users Group")
    plug = Organization.objects.create(
        name=g.name,
        group=g,
        description=" Linux is a free computer operating system. it runs on a large variety of computer hardware, and can be used for many purposes including desktop machines, small embedded systems and internet servers. you can find more information about Linux itself on the Linux international website. the Linux documentation project is also a good place to find general information about Linux.",
        phone_number="123-456-7890",
        available=False)
    plug.icon.save('plug.png', File(open(PIC_POPULATE_DIR+'plug.png')), 'r')

    g=Group.objects.create(name="Engineering Projects in Community Service")
    epics = Organization.objects.create(
        name=g.name,
        group=g,
        description=" Community service agencies face a future in which they must take advantage of technology to improve, coordinate, account for, and deliver the services they provide. they need the help of people with strong technical backgrounds. undergraduate students face a future in which they will need more than solid expertise in their discipline to succeed. they will be expected to work with people of many different backgrounds to identify and achieve goals. they need educational experiences that can help them broaden their skills. the challenge is to bring these two groups together in a mutually beneficial way. in response to this challenge, purdue university has created epics: engineering projects in community service",
        phone_number="123-456-7890",
        available=True)
    epics.icon.save('epics.png', File(open(PIC_POPULATE_DIR+'epics.png', 'r')))

    g=Group.objects.create(name="Association of Mechanical & Electrical Technologies")
    amet = Organization.objects.create(
        name=g.name,
        group=g,
        description="The association of mechanical and electrical technologists (amet) is an organization that brings science, technology, engineering, and mathematics (stem)-based students together to discuss and work on various extra-curricular projects throughout the school year. the group is meant to help educate students on what it is like to be in an interdisciplinary team and have fun at the same time. past and current projects include the following: gas grand prix, robosumo competitions, high altitude vehicle launches, a robotic assistant for people with limb paralysis, loudspeaker design / construction, and the national rube goldberg competition. along with projects, amet hosts various company sponsored lectures and recruitment efforts for our students.",
        phone_number="123-456-7890",
        available=False)
    amet.icon.save('amet.png', File(open(PIC_POPULATE_DIR+'amet.png', 'r')))

    #-------------- Users ------------------
    print '  creating Users'

    #create users
    emails = cycle(['evan@evanw.org',''])
    types = cycle([True,False])
    for num in range(0,10):
        newuser = User.objects.create(username='user{0}'.format(num))
        newuser.set_password('asdf')
        newuser.save()
        UserProfile.objects.create(user = newuser, purdueuser = types.next(),email = emails.next())

    #add Users to Organizations
    users = User.objects.all().exclude(username="AnonymousUser")
    for user in users[0:6]:
        if user.userprofile.purdueuser:
            plug.group.user_set.add(user)
            epics.group.user_set.add(user)
            amet.group.user_set.add(user)

    #--------------- Categories --------------------
    print '  creating Categories'

    #create categories
    categories=['engineering','computer science','construction','music','art','painting','linux','web development','iOS','Android']
    for category in categories:
       Category.objects.create( name=category,description='' ) 

    #tag Organizations with Cate
    plug.categories.add(Category.objects.get(name="computer science"), Category.objects.get(name="linux"))
    epics.categories.add(Category.objects.get(name = 'engineering'))
    amet.categories.add(Category.objects.get(name= 'engineering'))

    #--------------- Jobs --------------------
    print '  creating Jobs'

    #create Jobs
    jobs = ['Installing linux','Configuring vim','Make a website', 'Make a car', 'Finish circuit board', 'Finish software']

    community_partners = cycle([user_profile.user for user_profile in UserProfile.objects.filter(purdueuser=False)])
    client_orgs = cycle(["United Way","Lafayette Crisis Center","Jimbob's Hamburger Stand"])
    orgs = cycle(Organization.objects.all())

    #create JobRequests
    for job_name in jobs:
        print '    '+job_name
        job = Job.objects.create(name=job_name,
                                description = 'Description of the job',
                                deliverable = 'deliverable',
                                stakeholders = 'stakeholders',
                                tech_specs = 'tech specs',
                                budget = 'budget',
                                duedate = timezone.now(),
                                creator = community_partners.next(),
                                client_organization = client_orgs.next())
        #Make some jobrequests "randomly"
        if job.id % 2 == 0:
            jr = job.request_organization(orgs.next())
            # jr.decline()
        jr = job.request_organization(orgs.next())
        # jr.accept()
        jr = job.request_organization(orgs.next())

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'johnslist.settings')
    import django
    django.setup()
    if os.path.exists("db.sqlite3"):
        os.remove("db.sqlite3")
    call_command('makemigrations', interactive=True)
    call_command('migrate', interactive=True)
    call_command('migrate', 'dbtest', interactive=False)
    from django.core.files import File
    from dbtest.models import *
    from johnslist.settings import PIC_POPULATE_DIR
    from time import sleep
    populate()
