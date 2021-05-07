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
structure of incoming request, for reference
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
    metadata = migration_request['metadata']
    request_data = migration_request['request']
    apigee_mgmt_log = ApigeeMgmtLog(tenant_prefix=metadata['tenant-prefix'],
                                    destination=metadata['destination'],
                                    ip_addr=metadata['ipAddr'],
                                    username=metadata['username'],
                                    created_by=metadata['username'],
                                    user_roles=metadata['userRoles'],
                                    request_text=json.dumps(request_data),
                                    build_tags=request_data['buildTags'],
                                    build_comment=request_data['comment']
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
            if 'sharedflows' in request_data and request_data['sharedflows']:
                response_dict['sharedflows'] = migrate_shared_flows(request_data['sharedflows'], target_env=target_env),
            if 'proxies' in request_data and request_data['proxies']:
                response_dict['proxies'] = migrate_proxies(request_data['proxies'], target_env=target_env),
            if 'specs' in request_data and request_data['specs']:
                response_dict['specs'] = migrate_specs(request_data['specs'], target_env=target_env),
            if 'products' in request_data and request_data['products']:
                response_dict['products'] = migrate_products(request_data['products'], target_env=target_env)

            response_dict['result'] = {"SUCCESS": "Successfully migrated payload"}
            apigee_mgmt_log.status = 'success'
            status_code = 200

    except ValidationException as val_err:
        traceback.print_tb(val_err.__traceback__)
        response_dict["result"] = {"ERROR": f"{val_err}"}
        apigee_mgmt_log.status = 'invalid'
        status_code = 400

    except Exception as err:
        traceback.print_tb(err.__traceback__)
        response_dict["result"] = {"ERROR": f"{err}"}
        apigee_mgmt_log.status = 'error'
        status_code = 500

    finally:
        # add aggregated response to log and persist it
        apigee_mgmt_log.response_text = json.dumps(response_dict)
        apigee_mgmt_log.save()

        return JsonResponse(data=response_dict, status=status_code)
