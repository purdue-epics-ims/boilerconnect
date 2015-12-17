from django.core.management.base import BaseCommand, CommandError
from django.core.management import execute_from_command_line
import code

class Command(BaseCommand):
    help = "Imports models and guardian for testing. Also stores a user instance 'u', organization 'o', category 'c', and group 'g' for testing purposes."
    def handle(self, *args, **options):
        from guardian.shortcuts import assign_perm
        from dbtest.models import User,Organization,Job,Category,Group,JobRequest
        from django.utils import unittest
        from django.test import Client
        from notifications import notify
        from django.core.urlresolvers import reverse

        u = User.objects.get(id=1)
        u2 = User.objects.get(id=2)
        client = Client()
        o = Organization.objects.get(id=1)
        j = Job.objects.get(id=1)
        c = Category.objects.get(id=2)
        g = Group.objects.get(id=1)
        code.interact(local=locals())

