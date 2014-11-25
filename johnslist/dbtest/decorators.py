from django.http import HttpResponseRedirect
from johnslist.settings import REDIRECT_URL
from .models import *

#checks that a user is a member or admin of a specific organization
#only works if 'organization_id' is passed as an argument to the view on which this decorator is applied
def user_in_group(func):
	def wrapper(request,*args,**kwargs):
		organization = Organization.objects.get(id=kwargs['organization_id'])
		if request.user in organization.members.all() or request.user is organization.admin:
			return func(request,*args,**kwargs)
		else:
			return HttpResponseRedirect(REDIRECT_URL)
	return wrapper
