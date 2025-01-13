from bloomerp.utils.router import route
from django.urls import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from bloomerp.utils.filters import dynamic_filterset_factory
from bloomerp.utils.models import string_search_on_qs
from django.contrib.contenttypes.models import ContentType
from bloomerp.models import User, UserListViewPreference
from bloomerp.utils.models import model_name_plural_underline
from bloomerp.utils.model_io import BloomerpModelIO
from bloomerp.models import ApplicationField
from django.contrib.auth.decorators import login_required


@login_required
@route('data_table')
def data_table(request:HttpRequest) -> HttpResponse:
    """
    Component for rendering a data table.
    The data table can be filtered, searched, and paginated.
    
    Inputs:
    - data_table_content_type_id: The content type id of the model to be rendered in the data table
    - data_table_include_actions: Whether to include actions in the data table (update, delete, etc.)
    - data_table_string_search: A string to search for in the data table
    - data_table_download: If selected, the response will be a CSV or Excel download of the data table
    - data_table_foreign_key_field: The foreign key field to filter the data table by
    - data_table_foreign_key_value: The foreign key value to filter the data table by
    """
    user:User = request.user
    content_type_id = request.GET.get('data_table_content_type_id', None)
    include_actions = request.GET.get('data_table_include_actions', True) # Actions will be rendered to the right of the table for each row
    data_table_string_search = request.GET.get('data_table_string_search', None)
    data_table_download = request.GET.get('data_table_download', None)
    data_table_foreign_key_field = request.GET.get('data_table_foreign_key_field', None)
    data_table_foreign_key_value = request.GET.get('data_table_foreign_key_value', None)
    data_table_limit = request.GET.get('data_table_limit',25)


    # Set actions to True if the string is 'true'
    if include_actions in ['true', 'True']:
        include_actions = True
    else:
        include_actions = False
    
    # Get the model based on the content type id
    content_type = ContentType.objects.get(id=content_type_id)
    model = content_type.model_class()


    # Permissions check
    if not user.has_perm(f'{model._meta.app_label}.view_{model._meta.model_name}'):
        return HttpResponse('User does not have permission to view this data table')


    # Init the queryset
    qs = model.objects.all()

    # Filter the queryset by the foreign key field and value
    if data_table_foreign_key_field and data_table_foreign_key_value:
        qs = qs.filter(**{data_table_foreign_key_field: data_table_foreign_key_value})

    # Create the filterset using the dynamic_filterset_factory
    FilterSet = dynamic_filterset_factory(model)
    filterset = FilterSet(request.GET, queryset=qs)
    qs = filterset.qs

    # Get the list view preference for the user
    list_view_preferences = user.get_list_view_preference_for_model(model)
    
    if not list_view_preferences:
        list_view_preferences = UserListViewPreference.generate_default_for_user(user, content_type)

    # Apply string search
    if data_table_string_search:
        # Remove any leading or trailing whitespace
        data_table_string_search = data_table_string_search.strip()

        qs = string_search_on_qs(qs, data_table_string_search)

    # If the download parameter is set, return a CSV or Excel download
    if data_table_download == 'csv' or data_table_download == 'xlsx':
        fields = [pref.application_field.field for pref in list_view_preferences]
        

    if data_table_download == 'csv':
        model_io = BloomerpModelIO(model)
        file_bytes = model_io.export_to_csv(qs, fields)
        response = HttpResponse(file_bytes, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{model._meta.verbose_name_plural}_data.csv"'
        return response

    elif data_table_download == 'xlsx':
        model_io = BloomerpModelIO(model)
        file_bytes = model_io.export_to_excel(qs, fields)
        response = HttpResponse(file_bytes, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{model._meta.verbose_name_plural}_data.xlsx"'
        return response

    # Get the API endpoint for the model
    api_endpoint = reverse(model_name_plural_underline(model)+'-list')

    # Get the application fields
    application_fields = ApplicationField.objects.filter(
        content_type=ContentType.objects.get_for_model(model)
    ).exclude(
        field_type__in=['Property', 'AutoField','OneToManyField']
    )
    
    if data_table_limit:
        try:
            data_table_limit = int(data_table_limit)
            qs = qs[:data_table_limit]
        except:
            pass

    # Set permissions for the actions


    context = {
        'object_list': qs,
        'content_type_id': content_type_id,
        'list_view_preferences': list_view_preferences,
        'include_actions': include_actions,
        'api_endpoint': api_endpoint,
        'application_fields': application_fields,
        'data_table_foreign_key_field': data_table_foreign_key_field,
        'data_table_foreign_key_value': data_table_foreign_key_value,

        # Permissions
        'user_can_add': user.has_perm(f'{model._meta.app_label}.add_{model._meta.model_name}'),
        'user_can_change': user.has_perm(f'{model._meta.app_label}.change_{model._meta.model_name}'),
        'user_can_delete': user.has_perm(f'{model._meta.app_label}.delete_{model._meta.model_name}'),
        'user_can_bulk_change': user.has_perm(f'{model._meta.app_label}.bulk_change_{model._meta.model_name}'),
        'user_can_bulk_delete': user.has_perm(f'{model._meta.app_label}.bulk_delete_{model._meta.model_name}'),
        'user_can_bulk_add': user.has_perm(f'{model._meta.app_label}.bulk_add_{model._meta.model_name}'),
        'user_can_export': user.has_perm(f'{model._meta.app_label}.export_{model._meta.model_name}'),
    }

    return render(request, 'snippets/data_table.html', context)