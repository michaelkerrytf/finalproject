import json
import traceback

from django.http import JsonResponse

from .utils import TYPE_MAP, REQUEST_FACTORY, ARTIFACTS_WITH_REVISIONS, REQUEST_KEYS_NO_ARTIFACTS

from .env import Env
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

class ValidationException(Exception):
    def __init__(self, message="Validation Failed"):
        self.message = message
        super().__init__(self.message)


def validate_user_roles(migration_request: dict, target_env: Env):
    validation_dict = {}

    # check user roles for match with artifact prefix
    user_roles = migration_request['metadata']['userRoles']
    required_user_roles = set()
    user_role_prefixes = [role.split('-')[0] for role in user_roles]
    if user_roles and user_role_prefixes:
        for key in migration_request['request']:
            for artifact in migration_request['request'][key]:
                if key in ARTIFACTS_WITH_REVISIONS:
                    prefix = artifact['name'].split('-')[0]
                    artifact_name = artifact['name']
                else:
                    prefix = artifact.split('-')[0]
                    artifact_name = artifact
                required_user_roles.add(f"{prefix}-developer")
                if prefix not in user_role_prefixes:
                    if key not in validation_dict:
                        validation_dict[key] = {}
                    validation_dict[key][artifact_name] = "User missing valid roles to act on this artifact"

        # confirm that required user has required_user_roles in both source and target environment

        for role in required_user_roles:
            src_role_url = REQUEST_FACTORY.construct_url(org_name=target_env.get_src(),
                                                         artifact_name='userroles',
                                                         action='info',
                                                         param_dict={f'{TYPE_MAP["userroles"]}_name': role})
            dest_role_url = REQUEST_FACTORY.construct_url(org_name=target_env.get_dest(),
                                                          artifact_name='userroles',
                                                          action='info',
                                                          param_dict={f'{TYPE_MAP["userroles"]}_name': role})
            src_response = REQUEST_FACTORY.download(src_role_url)
            if migration_request['metadata']['username'] not in src_response.json():
                if 'userRoles' not in validation_dict:
                    validation_dict['userRoles'] = []
                validation_dict['userRoles'].append(f"User missing role {role} in source organization")
            dest_response = REQUEST_FACTORY.download(dest_role_url)
            if migration_request['metadata']['username'] not in dest_response.json():
                if 'userRoles' not in validation_dict:
                    validation_dict['userRoles'] = []
                validation_dict['userRoles'].append(f"User missing role {role} in destination organization")

    else:
        validation_dict['userRoles'] = "Missing user roles"

    return validation_dict


def validate_existence(migration_request: dict, target_env: Env):
    validation_dict = {}
    artifact_info_dict = {}
    for artifact_type in migration_request['request']:
        if artifact_type and artifact_type not in artifact_info_dict:
            artifact_info_dict[artifact_type] = []
        for artifact in migration_request['request'][artifact_type]:
            if artifact_type in ARTIFACTS_WITH_REVISIONS:
                artifact_name = artifact['name']
            else:
                artifact_name = artifact
            # retrieve artifact info from source env
            src_url = REQUEST_FACTORY.construct_url(org_name=target_env.get_src(),
                                                    artifact_name=artifact_type,
                                                    action='info',
                                                    param_dict={f'{TYPE_MAP[artifact_type]}_name': artifact_name})
            response = REQUEST_FACTORY.download(url=src_url)
            if response.status_code == 404:
                # artifact does not exist in source
                if artifact_type not in validation_dict:
                    validation_dict[artifact_type] = {}
                validation_dict[artifact_type][
                    artifact_name] = f"{artifact_type} with name '{artifact_name}' not found"

            elif response.status_code == 200:
                artifact_info = response.json()
                artifact_info_dict[artifact_type].append({artifact_name: artifact_info})
                # if artifact type has revision and revision is specified, verify that it exists
                if artifact_type in ARTIFACTS_WITH_REVISIONS:
                    if 'revision' in artifact:
                        if artifact['revision'] not in artifact_info['revision']:
                            # if it does not exist, throw validation error
                            if artifact_type not in validation_dict:
                                validation_dict[artifact_type] = {}
                            validation_dict[artifact_type][artifact_name] = f"Specified revision ({artifact['revision']}) does not exist in source org" # validation error
                    else:  # otherwise, set revision to latest
                        for artifact_to_update in migration_request['request'][artifact_type]: # this is a list of objects, need to find the right one
                            if artifact_to_update['name'] == artifact_name:
                                # extract latest revision number from shared flow info
                                artifact_to_update['revision'] = artifact_info['revision'][-1]
            else:
                # some other type of issue: failed validation
                if artifact_type not in validation_dict:
                    validation_dict[artifact_type] = {}
                validation_dict[artifact_type][artifact_name] = f"Call to Apigee Management API returned status code {response.status_code}"

    return validation_dict, artifact_info_dict

def validate_payload(migration_request: dict, target_env:Env):
    """
    validate that user has access to all artifacts via the roles associated with their api key
    verify that all artifacts exist in the source organization
    :param migration_request:
    :param target_env:
    :return:
    """
    validation_dict = validate_user_roles(migration_request, target_env)

    if validation_dict:  # there was some problem with user roles, so don't try to verify existence
        return validation_dict, {}
    # verify existence of artifacts in source org
    validation_dict, artifact_info_dict = validate_existence(migration_request, target_env)
    return  validation_dict, artifact_info_dict


def validate(migration_request: dict, target_env: Env = Env.STAGE):
    response_dict = {
        "result": {},
        "request": migration_request['request']
    }

    for key in REQUEST_KEYS_NO_ARTIFACTS:
        del migration_request['request'][key]

    try:
        validation_dict, artifact_info_dict = validate_payload(migration_request, target_env)
        response_dict['artifactInfo'] = artifact_info_dict
        if validation_dict:
            response_dict['validationResults'] = validation_dict
            raise ValidationException("VALIDATION FAILED! - see validationResults for details")
        response_dict["result"] = {"SUCCESS": "payload passed validation"}
        status_code = 200

    except ValidationException as val_err:
        traceback.print_tb(val_err.__traceback__)
        response_dict["result"] = {"ERROR": f"{val_err}"}
        status_code = 400

    except Exception as err:
        # need to figure out error display for failed validation
        traceback.print_tb(err.__traceback__)
        response_dict["result"] = {"ERROR": f"{err}"}
        status_code = 500

    return JsonResponse(data=response_dict, status=status_code)
