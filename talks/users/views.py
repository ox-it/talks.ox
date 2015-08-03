from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import permission_required, login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render, get_object_or_404, redirect

from datetime import date

from .models import Collection, TalksUserCollection, COLLECTION_ROLES_EDITOR, COLLECTION_ROLES_OWNER, COLLECTION_ROLES_READER
from .forms import CollectionForm


def webauth_logout(request):
    context = {'was_webauth': True}
    logout(request)
    return render_to_response('auth/logged_out.html', context)

@login_required
def manage_collections(request):
    context = {}
    if request.tuser:
        # Authenticated user
        if request.GET.get("public") == 'true':
            collections = Collection.objects.filter(public=True)
            context['viewing_public_lists'] = True
        else:
            collections = request.tuser.collections.all
        context['collections'] = collections
        context['user'] = request.tuser

    return render(request, 'users/collections.html', context)

@login_required
def view_collection(request, collection_slug):
    context = {}
    if request.tuser:
        # Authenticated user
        # TODO: Confirm that this user is allowed to view this list
        collection = Collection.objects.get(slug=collection_slug)
        context['collection'] = collection
        today = date.today()
        context['events'] = collection.get_events().filter(start__gte=today).order_by('start')
        context['event_groups'] = collection.get_event_groups().order_by('title')

    if request.GET.get('format') == 'txt':
        return render(request, 'users/collection_view.txt.html', context)
    else:
        return render(request, 'users/collection_view.html', context)

@login_required
def add_collection(request):
    context = {}
    if request.tuser:
        # Authenticated user
        context['collection_form'] = CollectionForm()

        if request.method == 'POST':
            context['collection_form'] = CollectionForm(request.POST)

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
    # TODO: Confirm that this user is allowed to edit this list
    collection = get_object_or_404(Collection, slug=collection_slug)
    if not collection.user_can_edit(request.user):
        raise PermissionDenied
    form = CollectionForm(request.POST or None, instance=collection, prefix='collection')
    context = {
        'collection': collection,
        'collection_form': form,
        'is_editing': True,
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
    # TODO: Confirm that this user is allowed to edit this list
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
