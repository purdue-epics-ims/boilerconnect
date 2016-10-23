from django.forms.widgets import SelectMultiple
from django.utils.html import format_html, html_safe
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.forms.utils import flatatt

from dbtest.models import *

# widget for searching and selecting organizations
class OrgSelect(SelectMultiple):
    input_type = None  # Subclasses must define this.

    def render(self, name, value, attrs=None):
        print "name:",name
        print "value:",value
        print "attrs:",attrs

        if value:
            selected_orgs = Organization.objects.filter(pk__in = value)
            deselected_orgs = Organization.objects.exclude(pk__in = value)
        else:
            selected_orgs = []
            deselected_orgs = Organization.objects.all()

        context = {
            'selected_orgs':selected_orgs,
            'deselected_orgs':deselected_orgs
        }
        return mark_safe(render_to_string('dbtest/org_search.html', context))
