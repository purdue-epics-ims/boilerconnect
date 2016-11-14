from django.contrib import admin
from .models import *

# Register your models here.

class JobAdmin(admin.ModelAdmin):
    model = Job
    list_filter = ('organizations__name',
                   'closed',
                   'categories',
                   'duedate',
    )
    list_display = ('name',
                    'closed',
                    'duedate',
    )

class CategoryAdmin(admin.ModelAdmin):
    model = Category
    list_filter = ('group__name',)

class OrganizationAdmin(admin.ModelAdmin):
    model = Organization
    list_filter = ('categories',
                   'available',
    )
    list_display = ('name',
                    'available',
    )


admin.site.register(Job,JobAdmin)
admin.site.register(Category,CategoryAdmin)
admin.site.register(CategoryGroup)
admin.site.register(Organization,OrganizationAdmin)
