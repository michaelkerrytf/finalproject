import os
import json

from django.http import JsonResponse, HttpResponse, Http404
from django.db import connections

# These views 'mock' the real Apigee Management API responses for the specific
# calls to migrate the 'adex-dummy-shared-flow'. I pulled them from the working
# version of our prototype that connects to the actual Apigee Management API


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
    :param request:
    :param org_name:
    :param sharedflow_name:
    :return:
    """
    if sharedflow_name == 'adex-dummy-shared-flow':
        return JsonResponse({
            "metaData": {
                "createdAt": 1617722163245,
                "createdBy": "mkerry@fas.harvard.edu",
                "lastModifiedAt": 1617722316447,
                "lastModifiedBy": "mkerry@fas.harvard.edu"
            },
            "name": "adex-dummy-shared-flow",
            "revision": [
                "1",
                "2"
            ]
        })
    else:
        return JsonResponse({'view': 'info',
                             'org_name': org_name,
                             'sharedflow_name': sharedflow_name})


def bundle(request, org_name, sharedflow_name: str, rev_no: int):
    """
    http://127.0.0.1:8000/apigee/organizations/harvard-preprod/sharedflows/adex-dummy-shared-flow/revisions/2?format=bundle

    :param request:
    :param org_name:
    :param sharedflow_name:
    :param rev_no:
    :return:
    """
    format_value = request.GET['format']  # will throw exception if param is missing
    if format_value != 'bundle':
        raise Http404
    filename = 'adex-dummy-shared-flow-bundle.zip'
    dir_path = os.path.dirname(os.path.realpath(__file__))
    zip_file = open(f"{dir_path}/files/{filename}", 'rb').read()
    response = HttpResponse(zip_file, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def post(request, org_name):
    action_value = request.POST['action']
    if action_value != 'import':
        raise Http404
    name_value = request.POST['name']
    if request.method == 'POST' and name_value == 'adex-dummy-shared-flow':
        return JsonResponse(
            {
                "basepaths": [],
                "configurationVersion": {
                    "majorVersion": 4, "minorVersion": 0
                },
                "contextInfo": "Revision 28 of application -NA-, in organization -NA-",
                "createdAt": 1620239321956,
                "createdBy": "apigee-nonprod-common@harvard.edu",
                "description": "for testing management api",
                "displayName": "adex-dummy-shared-flow",
                "entityMetaDataAsProperties": {
                    "bundle_type": "zip",
                    "lastModifiedBy": "apigee-nonprod-common@harvard.edu",
                    "createdBy": "apigee-nonprod-common@harvard.edu",
                    "lastModifiedAt": "1620239321956",
                    "subType": "null",
                    "createdAt": "1620239321956"
                },
                "lastModifiedAt": 1620239321956,
                "lastModifiedBy": "apigee-nonprod-common@harvard.edu",
                "manifestVersion": "SHA-512:f9ec561eba70e29c6e7e94bd6ff18cb849cbf0559f3e8e53eb3c1bf775d97a32a55fccb37d0988a0d6fc9472ed39c4373850750061a23bca28bbd36da6a60c00",
                "name": "adex-dummy-shared-flow",
                "policies": [
                    "adex-dummy-assign-message-policy"
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
            })
    else:
        return JsonResponse(
            {
                'view': 'post',
                'org_name': org_name,
                'shared_flow_name': name_value,
                'action': action_value
            }
        )


def deploy(request, org_name, env_name: str, sharedflow_name: str, rev_no: int):
    delay_value = request.GET['delay']
    force_value = request.GET['force']
    if sharedflow_name == 'adex-dummy-shared-flow':
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
        })
    else:
        return JsonResponse({
            'view': 'deploy',
            'org_name': org_name,
            'env_name': env_name,
            'sharedflow_name': sharedflow_name,
            'rev_no': rev_no,
            'delay': delay_value,
            'force': force_value})


def userinfo(request, org_name, userrole_name: str):
    """
    http://127.0.0.1:8000/apigee/organizations/harvard-preprod/userroles/adex-developer/users
    :param request:
    :param org_name:
    :param userrole_name:
    :return:
    """
    if userrole_name == 'adex-developer':
        return JsonResponse(['mkerry@fas.harvard.edu'], safe=False)
    else:
        return JsonResponse({'view': 'userinfo',
                             'org_name': org_name,
                             'userrole_name': userrole_name})


def assign(request, org_name, userrole_name: str):
    response_body = {
        'view': 'assign',
        'org_name': org_name,
        'userrole_name': userrole_name
    }
    if request.method == "POST":
        data = json.loads(request.body)
        if data['resourcePermission'][0]['path'] == '/sharedflows/adex-dummy-shared-flow':
            response_body = {
                "resourcePermission": [
                    {"path": "/sharedflows/adex-dummy-shared-flow", "permissions": ["delete", "get", "put"]},
                    {"path": "/sharedflows/adex-dummy-shared-flow/revisions/*", "permissions": ["delete", "get", "put"]},
                    {"path": "/environments/*/sharedflows/adex-dummy-shared-flow/revisions/*/deployments", "permissions": ["delete", "get", "put"]}
                ]
            }
        else:
            response_body['request'] = data
    return JsonResponse(response_body)


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
