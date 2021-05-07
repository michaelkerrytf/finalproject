import json

from django.shortcuts import HttpResponseRedirect, render
from django.http import JsonResponse
from django.db import connections
from django.views.decorators.csrf import csrf_exempt

from .env import Env
from .migrate.migrate import migrate
from .validate import validate
from .models import ApigeeMgmtLog

# Create your views here.


def success_response(message, status: int = 200):
    """
    helper to return success response
    :param message:
    :param status:
    :return:
    """
    return JsonResponse(data={"message": f"{message}"}, status=status)


def server_error(message:str, status:int = 500):
    return JsonResponse(data={"message": f"ERROR: {message}"}, status=status)


def method_unsupported(method):
    return server_error(message= f"{method} unsupported", status=405)


def bare_index(request):
    return HttpResponseRedirect('view/logs/all')


def index(request, tenant_prefix):
    """
    Renders the index page, which will display the logs via ajax call
    :param request:
    :param tenant_prefix:
    :return:
    """
    tenant_prefix_list = [item['tenant_prefix'] for item in list(ApigeeMgmtLog.objects.order_by('tenant_prefix').values('tenant_prefix').distinct().all())]
    return render(request, "logs/index.html", {
        'tenant_prefix': tenant_prefix,
        'tenant_prefix_list': tenant_prefix_list
    })


def health(request):
    """
    /health check DB connection
    :param request:
    :return:
    """
    conn = connections['default']
    try:
        conn.cursor()
        return JsonResponse({"message": "api is connected to db"})
    except Exception as err:
        return server_error('cannot connect to database')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def handle_migration_request(request, target_env: Env):
    """
    helper method for migration requests, applying error handling and calling the main migrate method
    :param request: 
    :param target_env: 
    :return: 
    """
    if target_env is None:
        return server_error("migration requires a target env", 400)
    if request.method == "GET":
        return JsonResponse({"migrate": target_env.value})
    if request.method == "POST":
        if request.body is not None:
            try:
                migration_request = json.loads(request.body)
                migration_request['destination'] = target_env.value
                if 'metadata' not in migration_request:
                    migration_request['metadata'] = {}
                if 'ipAddr' not in migration_request['metadata'] or not migration_request['metadata']['ipAddr']:
                    migration_request['metadata']['ipAddr'] = get_client_ip(request=request)
                return migrate(migration_request, target_env)
            except Exception as err:
                # log error to splunk
                return server_error(f"ERROR: {err}", 400)
        # log error to splunk
        return server_error(f"migration to {target_env.value} requires a json body", 400)
    return method_unsupported(request.method)


def handle_validation_request(request, target_env: Env):
    if target_env is None:
        return server_error("migration requires a target env", 400)
    if request.method == "GET":
        return JsonResponse({"validate": target_env.value})
    if request.method == "POST":
        if request.body is not None:
            try:
                migration_request = json.loads(request.body)
                migration_request['destination'] = target_env.value
                if 'metadata' not in migration_request:
                    migration_request['metadata'] = {}
                if 'ipAddr' not in migration_request['metadata'] or not migration_request['metadata']['ipAddr']:
                    migration_request['metadata']['ipAddr'] = get_client_ip(request=request)
                return validate(migration_request, target_env)
            except Exception as err:
                # log error to splunk
                return server_error(f"ERROR: {err}", 400)
        # log error to splunk
        return server_error(f"validation to {target_env.value} requires a json body", 400)
    return method_unsupported(request.method)


@csrf_exempt
def stage(request):
    return handle_migration_request(request, Env.STAGE)


@csrf_exempt
def validate_stage(request):
    return handle_validation_request(request, Env.STAGE)


@csrf_exempt
def prod(request):
    return handle_migration_request(request, Env.PROD)


@csrf_exempt
def validate_prod(request):
    return handle_validation_request(request, Env.PROD)


def return_logs_payload(logs_payload, count, offset, base_url):
    """
    helper to populate data for paginating logs
    :param count:
    :param offset:
    :param logs_payload:
    :param base_url:
    :return:
    """
    return JsonResponse(data={
        "count": count,
        "prev": f"{base_url}?offset={max(offset - 10, 0)}",
        "curr": f"{base_url}?offset={offset}",
        "next": f"{base_url}?offset={min(offset + 10, int((count-1)/10) * 10)}",
        "logs": [log.serialize() for log in logs_payload]
    }, safe=False, status=200)


@csrf_exempt
# @login_required
def logs(request, tenant_prefix):
    """
    returns paginated logs for tenant prefix, using offset (defaults to 0)
    :param request: 
    :param tenant_prefix: 
    :return: 
    """
    if "GET" == request.method:
        offset = max(int(request.GET.get('offset', 0)), 0)
        if tenant_prefix == 'all':
            count = ApigeeMgmtLog.objects.count()
            results = ApigeeMgmtLog.objects.order_by("-created_date").all()[offset:offset + 10]
        else:
            count = ApigeeMgmtLog.objects.filter(tenant_prefix=tenant_prefix).count()
            results = ApigeeMgmtLog.objects\
                .filter(tenant_prefix=tenant_prefix)\
                .order_by("-created_date")\
                .all()[offset:offset+10]
        return return_logs_payload(results, count, offset, request.build_absolute_uri(f'/api/migrate/logs/{tenant_prefix}'))
    return method_unsupported(request.method)
