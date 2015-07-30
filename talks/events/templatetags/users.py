from django import template

register = template.Library()


@register.filter()
def can_edit_event(user, event):
    return event.user_can_edit(user)

@register.filter()
def can_edit_group(user, group):
    return group.user_can_edit(user)

@register.filter()
def collection_contains_item(collection, item):
    # return true if collection contains item.
    # item can be an event or event_group
    return collection.contains_item(item)

