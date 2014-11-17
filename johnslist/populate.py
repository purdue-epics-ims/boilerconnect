cat << EOF
from dbtest.models import *

usernames = ['evan','tatparya','testing','user1','user2']
passwords = ['asdf','asdf','asdf','asdf','asdf']

print 'test'
for username,password in zip(usernames,passwords):
	user = User(username=user)
	user.set_password(password)
	print user.username,user.password

EOF
