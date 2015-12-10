from django import template

register = template.Library()

#------------ Inclusion Tags --------------
# Can be used in templates to functionally render some html

# render notifications in a panel
@register.inclusion_tag('tags/notifications.html')
def dash_notifications(title, notifications):
    unread = notifications.filter(unread=True)
    read = notifications.filter(unread=False)
    context = {'unread_notifications':unread,
               'read_notifications':read,
               'title':title
               }
    return context
