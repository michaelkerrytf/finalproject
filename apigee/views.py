import os

from django.http import JsonResponse, HttpResponse, Http404
from django.db import connections
from django.views.decorators.csrf import csrf_exempt

# These views 'mock' the real Apigee Management API responses for the specific
# calls to migrate the 'adex-dummy-shared-flow'. I pulled them from the working
# version of our prototype that connects to the actual Apigee Management API

# in addition, you can change the prefix from 'adex' to 'ats' or 'e33a' and the mock API
# 'should' still work :)


def health(request):
    """
    /health check DB connection
    :param request:
    :return:
    """
    conn = connections['default']
    try:
        conn.cursor()
        return JsonResponse({"message": "apigee is connected to database"})
    except Exception as err:
        return JsonResponse(data={"message": f"ERROR: apigee cannot connect to the database"}, status=500)


def info(request, org_name, sharedflow_name: str):
    """
    http://127.0.0.1:8000/apigee/organizations/harvard-preprod/sharedflows/adex-dummy-shared-flow/revisions/2?format=bundle
    in real API would provide information on the shared flow object for validation
    :param request:
    :param org_name:
    :param sharedflow_name:
    :return:
    """
    tenant_prefix = sharedflow_name.split('-')[0]
    return JsonResponse({
        "metaData": {
            "createdAt": 1617722163245,
            "createdBy": "mkerry@fas.harvard.edu",
            "lastModifiedAt": 1617722316447,
            "lastModifiedBy": "mkerry@fas.harvard.edu"
        },
        "name": f"{tenant_prefix}-dummy-shared-flow",
        "revision": [
            "1",
            "2"
        ]
    })


def bundle(request, org_name, sharedflow_name: str, rev_no: int):
    """
    http://127.0.0.1:8000/apigee/organizations/harvard-preprod/sharedflows/adex-dummy-shared-flow/revisions/2?format=bundle
    in real API would download shared flow bundle - here it uses a stored file for that purpose
    :param request:
    :param org_name:
    :param sharedflow_name:
    :param rev_no:
    :return:
    """
    tenant_prefix=sharedflow_name.split('-')[0]
    format_value = request.GET['format']  # will throw exception if param is missing
    if format_value != 'bundle':
        raise Http404
    filename = f'{tenant_prefix}-dummy-shared-flow-bundle.zip'
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f"{dir_path}/files/{filename}", 'rb') as fh:
        zip_file = fh.read()
    response = HttpResponse(zip_file, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@csrf_exempt
def post(request, org_name):
    """
    in real API would upload and create the shared flow in the target env
    :param request:
    :param org_name:
    :return:
    """
    action_value = request.GET['action']
    if action_value != 'import':
        raise Http404
    name_value = request.GET['name']
    tenant_prefix = name_value.split('-')[0]
    if org_name == 'harvard':
        response_org_name = 'preprod'
    else:
        response_org_name = 'nonprod'

    return JsonResponse(
        {
            "basepaths": [],
            "configurationVersion": {
                "majorVersion": 4, "minorVersion": 0
            },
            "contextInfo": "Revision 28 of application -NA-, in organization -NA-",
            "createdAt": 1620239321956,
            "createdBy": f"apigee-{response_org_name}-common@harvard.edu",
            "description": "for testing management api",
            "displayName": f"{tenant_prefix}-dummy-shared-flow",
            "entityMetaDataAsProperties": {
                "bundle_type": "zip",
                "lastModifiedBy": f"apigee-{response_org_name}-common@harvard.edu",
                "createdBy": f"apigee-{response_org_name}-common@harvard.edu",
                "lastModifiedAt": "1620239321956",
                "subType": "null",
                "createdAt": "1620239321956"
            },
            "lastModifiedAt": 1620239321956,
            "lastModifiedBy": f"apigee-{response_org_name}-common@harvard.edu",
            "manifestVersion": "SHA-512:f9ec561eba70e29c6e7e94bd6ff18cb849cbf0559f3e8e53eb3c1bf775d97a32a55fccb37d0988a0d6fc9472ed39c4373850750061a23bca28bbd36da6a60c00",
            "name": f"{tenant_prefix}-dummy-shared-flow",
            "policies": [
                f"{tenant_prefix}-dummy-assign-message-policy"
            ],
            "proxies": [],
            "resourceFiles": {
                "resourceFile": []
            },
            "resources": [],
            "revision": "28",
            "sharedFlows": ["default"],
            "spec": "",
            "targetServers": [],
            "targets": [],
            "type": "Application"
        }, status=201)


@csrf_exempt
def deploy(request, org_name, env_name: str, sharedflow_name: str, rev_no: int):
    """
    in real API would cause the shared flow to be deployed to the target env
    :param request:
    :param org_name:
    :param env_name:
    :param sharedflow_name:
    :param rev_no:
    :return:
    """
    # these query params are required, so if missing will cause an exception
    delay_value = request.GET['delay']
    force_value = request.GET['force']
    return JsonResponse({
        "environment": f"{env_name}",
        "name": f"{rev_no}",
        "organization": f"{org_name}",
        "revision": f"{rev_no}",
        "server": [{
            "pod": {
                "name": "pausf914f4f0",
                "region": "us-east-1"
            },
            "status": "deployed",
            "type": ["message-processor"],
            "uUID": "9e62531e-518f-4d86-b561-3225f331ef9c"
        },
            {"pod": {
                "name": "pausf914f4f0",
                "region": "us-east-1"
            },
                "status": "deployed",
                "type": ["message-processor"],
                "uUID": "9976ecdf-9a11-44f4-bb35-6e1694ee5539"}
        ],
        "sharedFlow": f"{sharedflow_name}",
        "state": "deployed"
    }, status=200)


def userinfo(request, org_name, userrole_name: str):
    """
    http://127.0.0.1:8000/apigee/organizations/harvard-preprod/userroles/adex-developer/users
    in real API used for userrole lookup for validation
    :param request:
    :param org_name:
    :param userrole_name:
    :return:
    """
    if userrole_name == 'adex-developer':
        users = ['mkerry@fas.harvard.edu']
    elif userrole_name == 'ats-developer':
        users = ['mkerry@fas.harvard.edu']
    else:  # e33a-developer
        users = ['mkerry@fas.harvard.edu', 'lok026@g.harvard.edu']

    return JsonResponse(users, safe=False)


@csrf_exempt
def assign(request, org_name, userrole_name: str):
    """
    in real API sets appropriate permissions on shared flow in target env
    :param request:
    :param org_name:
    :param userrole_name:
    :return:
    """
    tenant_prefix = userrole_name.split('-')[0]
    response_body = {
        "resourcePermission": [
            {"path": f"/sharedflows/{tenant_prefix}-dummy-shared-flow", "permissions": ["delete", "get", "put"]},
            {"path": f"/sharedflows/{tenant_prefix}-dummy-shared-flow/revisions/*", "permissions": ["delete", "get", "put"]},
            {"path": f"/environments/*/sharedflows/{tenant_prefix}-dummy-shared-flow/revisions/*/deployments", "permissions": ["delete", "get", "put"]}
        ]
    }

    return JsonResponse(response_body, status=201)


# here's an example of a successful migration in the real system
full_success_response = {
    "result": {
        "SUCCESS": "Successfully migrated payload"
    },
    "sharedflows":
        {"adex-dummy-shared-flow": {
            "upload": {"basepaths": [], "configurationVersion": {"majorVersion": 4, "minorVersion": 0},
                       "contextInfo": "Revision 28 of application -NA-, in organization -NA-", "createdAt": 1620239321956,
                       "createdBy": "apigee-nonprod-common@harvard.edu", "description": "for testing management api",
                       "displayName": "adex-dummy-shared-flow", "entityMetaDataAsProperties": {"bundle_type": "zip",
                                                                                               "lastModifiedBy": "apigee-nonprod-common@harvard.edu",
                                                                                               "createdBy": "apigee-nonprod-common@harvard.edu",
                                                                                               "lastModifiedAt": "1620239321956",
                                                                                               "subType": "null",
                                                                                               "createdAt": "1620239321956"},
                       "lastModifiedAt": 1620239321956, "lastModifiedBy": "apigee-nonprod-common@harvard.edu",
                       "manifestVersion": "SHA-512:f9ec561eba70e29c6e7e94bd6ff18cb849cbf0559f3e8e53eb3c1bf775d97a32a55fccb37d0988a0d6fc9472ed39c4373850750061a23bca28bbd36da6a60c00",
                       "name": "adex-dummy-shared-flow", "policies": ["adex-dummy-assign-message-policy"], "proxies": [],
                       "resourceFiles": {"resourceFile": []}, "resources": [], "revision": "28", "sharedFlows": ["default"],
                       "spec": "", "targetServers": [], "targets": [], "type": "Application"},
            "deploy": {"environment": "stage", "name": "28", "organization": "harvard-preprod", "revision": "28", "server": [
                {"pod": {"name": "pausf914f4f0", "region": "us-east-1"}, "status": "deployed", "type": ["message-processor"],
                 "uUID": "9e62531e-518f-4d86-b561-3225f331ef9c"},
                {"pod": {"name": "pausf914f4f0", "region": "us-east-1"}, "status": "deployed", "type": ["message-processor"],
                 "uUID": "9976ecdf-9a11-44f4-bb35-6e1694ee5539"}], "sharedFlow": "adex-dummy-shared-flow", "state": "deployed"},
            "assignRole": {
                "resourcePermission": [{"path": "/sharedflows/adex-dummy-shared-flow", "permissions": ["delete", "get", "put"]},
                                       {"path": "/sharedflows/adex-dummy-shared-flow/revisions/*",
                                        "permissions": ["delete", "get", "put"]},
                                       {"path": "/environments/*/sharedflows/adex-dummy-shared-flow/revisions/*/deployments",
                                        "permissions": ["delete", "get", "put"]}]
            }}}

}
