from django import template

register = template.Library()


@register.filter()
def can_edit_event(user, event):
    return event.user_can_edit(user)

@register.filter()
def can_edit_group(user, group):
    return group.user_can_edit(user)