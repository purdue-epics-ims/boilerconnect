import os
from django.core.management import call_command

def populate():
    #add Users
    if os.path.exists("db.sqlite3"):
        os.remove("db.sqlite3")
    call_command('syncdb', interactive=False)
    
    for num in range(0,20):
        newuser = User.objects.create(username='user{0}'.format(num))
        newuser.set_password('asdf')
        newuser.save()

    #add Organizations
    g=Group.objects.create(name="Purdue Linux Users Group")
    plug = Organization.objects.create(
        name=g.name,
        group=g,
        description=" Linux is a free computer operating system. it runs on a large variety of computer hardware, and can be used for many purposes including desktop machines, small embedded systems and internet servers. you can find more information about Linux itself on the Linux international website. the Linux documentation project is also a good place to find general information about Linux.",
        email="president@purduelug.org",
        phone_number="123-456-7890",
        available=False)
    plug.icon.save('plug.png', File(open(PIC_POPULATE_DIR+'plug.png')), 'r')
        

    g=Group.objects.create(name="Engineering Projects in Community Service")
    epics = Organization.objects.create(
        name=g.name,
        group=g,
        description=" Community service agencies face a future in which they must take advantage of technology to improve, coordinate, account for, and deliver the services they provide. they need the help of people with strong technical backgrounds. undergraduate students face a future in which they will need more than solid expertise in their discipline to succeed. they will be expected to work with people of many different backgrounds to identify and achieve goals. they need educational experiences that can help them broaden their skills. the challenge is to bring these two groups together in a mutually beneficial way. in response to this challenge, purdue university has created epics: engineering projects in community service",
        email="epics@purdue.edu",
        phone_number="123-456-7890",
        available=True)
    epics.icon.save('epics.png', File(open(PIC_POPULATE_DIR+'epics.png', 'r')))

    g=Group.objects.create(name="Association of Mechanical & Electrical Technologies")
    amet = Organization.objects.create(
        name=g.name,
        group=g,
        description="The association of mechanical and electrical technologists (amet) is an organization that brings science, technology, engineering, and mathematics (stem)-based students together to discuss and work on various extra-curricular projects throughout the school year. the group is meant to help educate students on what it is like to be in an interdisciplinary team and have fun at the same time. past and current projects include the following: gas grand prix, robosumo competitions, high altitude vehicle launches, a robotic assistant for people with limb paralysis, loudspeaker design / construction, and the national rube goldberg competition. along with projects, amet hosts various company sponsored lectures and recruitment efforts for our students.",
        email="ahaberly@purdue.edu",
        phone_number="123-456-7890",
        available=False)
    amet.icon.save('amet.png', File(open(PIC_POPULATE_DIR+'amet.png', 'r')))

    #add Users to Organizations
    users = User.objects.all().exclude(username="AnonymousUser")
    for user in users[0:6]:
        plug.group.user_set.add(user)
        epics.group.user_set.add(user)
        amet.group.user_set.add(user)

    #set is_admin
    u = User.objects.get(pk=1)
    for org in Organization.objects.all():
        assign_perm('is_admin',u,org)
        assign_perm('edit_organization',u,org)


    #add ServiceServiceCategory's
    categories=['engineering','computer science','construction','music','art','painting','linux','web development','iOS','Android']
    for category in categories:
       Category.objects.create( name=category,description='' ) 

    plug.categories.add(Category.objects.get(name="computer science"), Category.objects.get(name="linux"))
    epics.categories.add(Category.objects.get(name = 'engineering'))
    amet.categories.add(Category.objects.get(name= 'engineering'))
    
    #add Jobs
    jobs = ['Installing linux','Configuring vim','Make a website', 'Make a car', 'Finish circuit board', 'Finish software']
    user_num = 1
    org_num = 1
    acc = True

    for job in jobs:
        Job.objects.create(name=job, description = 'Description of the job', duedate = '2015-3-21', creator = User.objects.get(id = user_num))
        Job.objects.get(id = user_num).setUpJobrelation(Organization.objects.get(id = org_num))
        if acc == False:
            org_num += 1
            acc = True
        else:
            jr = Jobrelation.objects.get(job=Job.objects.get(id=user_num),organization = Organization.objects.get(id=org_num))
            jr.accepted = True
            jr.save()
            acc = False
        user_num += 1

if __name__ == '__main__':
        
    print 'Populating database...'
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'johnslist.settings')
    from django.core.files import File
    from dbtest.models import *
    from johnslist.settings import PIC_POPULATE_DIR
    from time import sleep
    import django
    django.setup()
    populate()
