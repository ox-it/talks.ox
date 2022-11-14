from __future__ import absolute_import
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import permission_required, login_required
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render, get_object_or_404, redirect

from datetime import date

from .models import Collection, TalksUser, TalksUserCollection, COLLECTION_ROLES_EDITOR, COLLECTION_ROLES_OWNER, COLLECTION_ROLES_READER
from talks.events.models import Event
from talks.events.views import group_events
from talks.users.authentication import user_in_group_or_super
from talks.events.datasources import DEPARTMENT_DATA_SOURCE
from .forms import CollectionForm

def shibboleth_logout(request):
    context = {'was_shibboleth': True}
    logout(request)
    return render('auth/logged_out.html', context)


@login_required
def manage_collections(request):
    context = {}
    if request.tuser:
        # Authenticated user
        context['collections_owner'] = request.tuser.collections.filter(talksusercollection__role=COLLECTION_ROLES_OWNER).distinct().order_by('title')
        context['collections_editor'] = request.tuser.collections.filter(talksusercollection__role=COLLECTION_ROLES_EDITOR).distinct().order_by('title')
        context['collections_reader'] = request.tuser.collections.filter(talksusercollection__role=COLLECTION_ROLES_READER).distinct().order_by('title')
        context['collection_type_filters'] = COLLECTION_ROLES_OWNER, COLLECTION_ROLES_EDITOR, COLLECTION_ROLES_READER

        context['user_is_a_contributor'] = user_in_group_or_super(request.user)

    return render(request, 'users/collections.html', context)


def list_public_collections(request):
    context = {}
    context['collections'] = Collection.objects.filter(public=True).order_by('title')

    return render(request, 'users/public_collections.html', context)

def browse_public_collections(request):
    context = {}
    context['collections'] = Collection.objects.filter(public=True).order_by('title')

    return render(request, 'users/collection_list.html', context)

def view_collection(request, collection_slug):
    collection = Collection.objects.get(slug=collection_slug)
    if collection.public:
        pass
    elif not collection.user_can_view(request.user):
        raise PermissionDenied

    show_all = request.GET.get('show_all', False)
    allEvents = collection.get_all_events().order_by('start')


    if not show_all:
        allEvents = allEvents.filter(start__gte=date.today())

    grouped_events = group_events(allEvents)

    series = collection.get_event_groups().order_by('title')

    collectedDeps = collection.get_departments().exclude(department='oxpoints:23232729').exclude(department='oxpoints:23232677')
    departments = map(lambda cdep:DEPARTMENT_DATA_SOURCE.get_object_by_id(cdep.department), collectedDeps)

    collectionContributors = None
    if request.tuser:
        collectionContributors = TalksUser.objects.filter(talksusercollection__collection=collection, talksusercollection__role=COLLECTION_ROLES_EDITOR)

    collectionOwner = None
    if request.tuser:
        collectionOwner = TalksUser.objects.filter(talksusercollection__collection=collection, talksusercollection__role=COLLECTION_ROLES_OWNER)

    context = {
        'collection' : collection,
        'show_all' : show_all,
        'events' : allEvents,
        'grouped_events': grouped_events,
        'event_groups' : series,
        'contributors' : collectionContributors,
        'departments' : departments,
        'owner': collectionOwner
    }

    if request.GET.get('format') == 'txt':
        return render(request, 'users/collection_view.txt.html', context)
    else:
        return render(request, 'users/collection_view.html', context)



@login_required
def my_talks(request):
    grouped_events = None
    collections = request.tuser.collections.all()
    if collections:
            user_events = collections[0].get_all_events()
            for collection in collections[1:]:
                user_events = user_events | collection.get_all_events()
            #context['collections'] = collections
            user_events = user_events.filter(start__gte=date.today())
            grouped_events = group_events(user_events)

    context = {
        'grouped_events': grouped_events
    }

    if request.GET.get('format') == 'txt':
        return render(request, 'users/my_talks.txt.html', context)
    else:
        return render(request, 'users/my_talks.html', context)



@login_required
def add_collection(request):
    context = {}
    if request.tuser:
        # Authenticated user
        context['collection_form'] = CollectionForm()
        if (not user_in_group_or_super(request.user)):
            del context['collection_form'].fields['editor_set']

        if request.method == 'POST':
            context['collection_form'] = CollectionForm(request.POST)
            if (not user_in_group_or_super(request.user)):
                del context['collection_form'].fields['editor_set']

            forms_valid = context['collection_form'].is_valid()
            if forms_valid:
                collection = context['collection_form'].save()
                TalksUserCollection.objects.create(user=request.tuser,
                                        collection=collection,
                                        role=COLLECTION_ROLES_OWNER)
                messages.success(request, "A new list has been created")
                return HttpResponseRedirect(reverse('manage-lists'))
            else:
                messages.warning(request, "Please correct errors below")

    return render(request, 'users/collection_form.html', context)

@login_required
def edit_collection(request, collection_slug):
    collection = get_object_or_404(Collection, slug=collection_slug)
    if not collection.user_can_edit(request.user):
        raise PermissionDenied

    # Limit editor set to users who only have editor role.
    editors = TalksUserCollection.objects.filter(collection=collection, role=COLLECTION_ROLES_EDITOR).values_list('user_id', flat=True)
    editor_set = {'editor_set': editors}
    form = CollectionForm(request.POST or None, instance=collection, prefix='collection', initial=editor_set)

    if (not user_in_group_or_super(request.user)):
        del form.fields['editor_set']

    context = {
        'collection': collection,
        'collection_form': form,
        'is_editing': True,
        'user_is_a_contributor': user_in_group_or_super(request.user),
    }
    if request.method == 'POST':
        if form.is_valid():
            collection = form.save()
            messages.success(request, "List '" + collection.title + "' was updated")
            return HttpResponseRedirect(reverse('manage-lists'))
        else:
            messages.warning(request, "Please correct errors below")
    return render(request, "users/collection_form.html", context)

@login_required
def delete_collection(request, collection_slug):
    collection = get_object_or_404(Collection, slug=collection_slug)
    if not collection.user_can_edit(request.user):
        raise PermissionDenied

    context = {
        'collection': collection,
    }
    if request.method == 'POST':
        collection.delete()
        messages.success(request, "List has been successfully deleted")
        return redirect('manage-lists')
    return render(request, "users/collection_delete.html", context)
