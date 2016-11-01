from django.forms.widgets import SelectMultiple, CheckboxSelectMultiple
from django.utils.html import format_html, html_safe
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.forms.utils import flatatt

from dbtest.models import *

# widget for searching and selecting organizations
class OrgSelect(SelectMultiple):
    input_type = None  # Subclasses must define this.

    def render(self, name, value, attrs=None):

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
        return mark_safe(render_to_string('widgets/org_search.html', context))

# widget for displaying checkboxes for categories by group
class CategorySelect(CheckboxSelectMultiple):
    input_type = None  # Subclasses must define this.

    def render(self, name, value, attrs=None):

        context = {
            'category_groups':CategoryGroup.objects.all(),
            'selected_categories':Category.objects.filter(id__in = value)
            }
        return mark_safe(render_to_string('widgets/category_select.html', context))
