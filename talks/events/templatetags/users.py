from django import template

register = template.Library()


@register.filter()
def can_edit(user, event):
    return event.user_can_edit(user)
