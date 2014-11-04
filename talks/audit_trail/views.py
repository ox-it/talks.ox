from datetime import datetime

import django
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from reversion.models import Revision
import reversion

from .forms import RevisionsFilteringForm
from .utils import (compare_dicts, find_user_friendly_rel, find_user_friendly_many,
                    find_user_friendly_display_name)


def database_usage(request):
    INITIAL_PAGE = 1
    DEFAULT_COUNT = 20

    all_revisions = Revision.objects.all().order_by('-date_created').select_related('user')

    # removing pagination arguments from the form
    # they need to be processed separately as the form might be empty
    form_args = request.GET.copy()
    if form_args.has_key('page'):
        del form_args['page']
    if form_args.has_key('count'):
        del form_args['count']

    form = RevisionsFilteringForm(form_args)
    if form.is_valid():
        from_date = form.cleaned_data['from_date']
        to_date = form.cleaned_data['to_date']
        if from_date:
            all_revisions = all_revisions.filter(date_created__gte=from_date)
        if to_date:
            # search for full day, change hour to midnight
            to_date = datetime(to_date.year, to_date.month, to_date.day, 23, 59, 59)
            all_revisions = all_revisions.filter(date_created__lte=to_date)
    else:
        form = RevisionsFilteringForm()

    page = request.GET.get('page', INITIAL_PAGE)
    count = request.GET.get('count', DEFAULT_COUNT)

    paginator = Paginator(all_revisions, count)

    try:
        revisions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        revisions = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        revisions = paginator.page(paginator.num_pages)

    context = RequestContext(request, {
        'revisions': revisions,
        'pagination_count': count,
        'form': form
    })
    return render_to_response('audit_trail/database_usage.html', context)


def revision_details(request, revision_id):
    revision = Revision.objects.get(id=revision_id)

    current_versions = revision.version_set.all()
    diffs = []
    for version in current_versions:
        diff, compared_values = _get_version_diff(version)
        diffs.append((diff, compared_values))

    context = RequestContext(request, {
        'revision': revision,
        'diffs': diffs,
    })
    return render_to_response('audit_trail/view_revision.html', context)


def _get_version_diff(version):
    """Get the difference betwee
    :param version: reversion.Version object
    :return: tuple (metadata as dict, compared values as dict)
    """
    ident = version.field_dict['id']
    model = version.content_type.model_class()
    # uses the class rather than the instance so that we can also work with deleted objects
    all_versions = reversion.get_for_object_reference(model, ident).select_related('revision__user')
    all_versions = list(all_versions)
    diff = {}
    diff['object_name'] = model.__name__

    fields = {}
    foreign_keys = {}
    many_to_manys = {}
    choices_display = {}    # CharField having a list of choices

    for field in model._meta.fields:
        fields[field.name] = field
        if type(field) is django.db.models.fields.related.ForeignKey:
            foreign_keys[field.name] = field
        elif type(field) is django.db.models.fields.CharField and field.choices:
            choices_display[field.name] = field
        elif type(field) is django.db.models.fields.TextField and field.choices:
            choices_display[field.name] = field
    for field in model._meta.many_to_many:
        fields[field.name] = field
        if type(field) is django.db.models.fields.related.ManyToManyField:
            many_to_manys[field.name] = field

    try:
        previous_version = all_versions[all_versions.index(version)+1]
        diff['has_previous'] = True
        if previous_version.revision.user:
            diff['previous_user'] = previous_version.revision.user.email
        else:
            diff['previous_user'] = 'System'
        diff['previous_date'] = previous_version.revision.date_created
        diff['previous_comment'] = previous_version.revision.comment
        compared = compare_dicts(version.field_dict, previous_version.field_dict)
    except IndexError:
        diff['has_previous'] = False
        compared = compare_dicts(version.field_dict, None)

    # stores an association between the type of fields
    # available and the function to transform the value
    transform_fields = [
        (foreign_keys, find_user_friendly_rel),
        (many_to_manys, find_user_friendly_many),
        (choices_display, find_user_friendly_display_name)]

    compared_values = _build_compared_values(compared, fields, transform_fields)
    return diff, compared_values


def _build_compared_values(compared, fields, transformations):
    """Build a dictionary containing the compared values
    augmented to be user-friendly
    :param compared: dictionary of compared values
    :param fields: dictionary of fields available
    :param transformations: list of tuples containing functions to transform content
    :return: dictionary of compared values
    """
    compared_values = {}
    for field_name, values in compared.items():
        # attempt to follow foreign keys and many-to-manys to
        # retrieve user-friendly values...
        for type_of_field, transform_func in transformations:
            if field_name in type_of_field:
                new_text = transform_func(type_of_field[field_name], values[0])
                old_text = transform_func(type_of_field[field_name], values[1])
                values = (new_text, old_text, values[2])
                break

        # try to replace by verbose name if there is one
        if field_name in fields and hasattr(fields[field_name], 'verbose_name'):
            verbose_name = fields[field_name].verbose_name
            compared_values[verbose_name] = values
        else:
            compared_values[field_name] = values
    return compared_values
