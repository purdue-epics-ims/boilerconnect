from django.shortcuts import render
from johnslist.settings import REDIRECT_URL
from .models import *

#general purpose decorator to check if user can access various objects
def user_has_perm(perm):
    def decorator(func):
        def wrapper(request,*args,**kwargs):
            success = False

            user = request.user

            #check if user has perm for Organization
            if 'organization_id' in kwargs.keys():
                organization = Organization.objects.get(id=kwargs['organization_id'])
                if user.has_perm(perm,organization):
                    success = True

            #or, check if user has perm for Job
            elif 'job_id' in kwargs.keys():
                job = Job.objects.get(id=kwargs['job_id'])
                if user.has_perm(perm,job):
                    success = True

            #or, check if user has perm for User
            elif 'user_id' in kwargs.keys():
                user = User.objects.get(id=kwargs['user_id'])
                if request.user == user:
                    success = True

            if success == True:
                return func(request,*args,**kwargs)
            else:
                return render(request,'dbtest/confirm.html',{'title':'Permission Denied','message':'You do not have access to this resource'})
        return wrapper
    return decorator
