import json
import traceback

from django.http import JsonResponse

from ..models import ApigeeMgmtLog
from ..env import Env
from ..utils import REQUEST_KEYS_NO_ARTIFACTS
from ..validate import validate_payload, ValidationException
from .sharedflows import migrate_shared_flows
from .proxies import migrate_proxies
from .specs import migrate_specs
from .products import migrate_products

"""
structure of incoming request
{
    "metadata": { // added by apigee
        "tenant-prefix": "", // maybe not?
        "username":"", // maybe?
        "userRoles": [],
        "ipAddr": ""
    },
    "request": {
        "buildTags":"",
        "comment":"",
	    "sharedflows":[
	        {
	            'name': 'ats-shared-flow'
	            'revision': '1'  // OPTIONAL defaults to latest. however, if revision is supplied, existence will be validated
	        }
	    ],
	    "proxies":[
	        {
	            'name': 'ats-proxy'
	            'revision': '2' // OPTIONAL defaults to latest. however, if revision is supplied, existence will be validated
	        }
	    ],
	    "products":['ats-product-1', 'ats-product-2'],
	    "specs":['ats-spec-1']
    }
} 
"""


def migrate(migration_request: dict, target_env: Env = Env.STAGE):
    """
    use Env.value as key in MIGRATION_MAP for apigee organizations for src and dest organizations
    create initial log with request
    capture IP address, too, and add that
    add tenant prefix / username, depending
    orchestrate calls to migrate different artifacts, aggregate responses, add that to log as response_text
    :param migration_request:
    :param target_env:
    :return:
    """
    apigee_mgmt_log = ApigeeMgmtLog(tenant_prefix=migration_request['metadata']['tenant-prefix'],
                                    ip_addr=migration_request['metadata']['ipAddr'],
                                    username=migration_request['metadata']['username'],
                                    created_by=migration_request['metadata']['username'],
                                    user_roles=migration_request['metadata']['userRoles'],
                                    request_text=json.dumps(migration_request['request']),
                                    build_tags=migration_request['request']['buildTags'],
                                    build_comment=migration_request['request']['comment']
                                    )
    # once logged, remove comment and buildTags
    for key in REQUEST_KEYS_NO_ARTIFACTS:
        del migration_request['request'][key]
    # how to handle failed validation?
    response_dict = { "result": {} }

    try:
        validation_dict, artifact_info_dict = validate_payload(migration_request, target_env)
        if validation_dict:
            response_dict['validationResults'] = validation_dict
            response_dict['artifactInfo'] = artifact_info_dict
            raise ValidationException("VALIDATION FAILED! - see validationResults for details")
        else:
            # validation passed; migrate all
            if 'sharedflows' in migration_request['request'] and migration_request['request']['sharedflows']:
                response_dict['sharedflows'] = migrate_shared_flows(migration_request['request']['sharedflows'], target_env=target_env),
            if 'proxies' in migration_request['request'] and migration_request['request']['proxies']:
                response_dict['proxies'] = migrate_proxies(migration_request['request']['proxies'], target_env=target_env),
            if 'specs' in migration_request['request'] and migration_request['request']['specs']:
                response_dict['specs'] = migrate_proxies(migration_request['request']['specs'], target_env=target_env),
            if 'products' in migration_request['request'] and migration_request['request']['products']:
                response_dict['products'] = migrate_proxies(migration_request['request']['products'], target_env=target_env)

            response_dict['result'] = {"SUCCESS": "Successfully migrated payload"}
            status_code = 200

    except ValidationException as val_err:
        traceback.print_tb(val_err.__traceback__)
        response_dict["result"] = {"ERROR": f"{val_err}"}
        status_code = 400

    except Exception as err:
        traceback.print_tb(err.__traceback__)
        response_dict["result"] = {"ERROR": f"{err}"}
        status_code = 500

    # add aggregated response to log and persist it
    apigee_mgmt_log.response_text = json.dumps(response_dict)
    apigee_mgmt_log.save()

    return JsonResponse(data=response_dict, status=status_code)
