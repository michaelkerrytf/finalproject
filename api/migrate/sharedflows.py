import os

from ..utils import REQUEST_FACTORY, TYPE_MAP
from ..env import Env


def migrate_shared_flows(shared_flow_list: list, target_env:Env) -> list:
    """
    migrate from source organization to target
    construct response list of json responses
    :param shared_flow_list:
    :param target_env:
    :return:
    """
    response_log = []

    for shared_flow in shared_flow_list:  # shared_flow is an object: {'name': '', 'revision': ''}
        response_log_entry = {}
        shared_flow_name = shared_flow['name']
        filename = REQUEST_FACTORY.endpoint_info['sharedflows']['filename']
        rev_no = shared_flow['revision']  # rev_no has been added this dict during validation if not already present
        try:
            # retrieve bundle from that revision number
            download_url = REQUEST_FACTORY.construct_url(org_name=target_env.get_src(),
                                                         artifact_name='sharedflows',
                                                         action='download',
                                                         param_dict={'sharedflow_name': shared_flow_name, 'rev_no': rev_no})
            bundle = REQUEST_FACTORY.download(url=download_url)
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(f"{dir_path}/files/{filename}", "wb") as file:
                file.write(bundle.content)

            # post bundle to target env
            upload_url = REQUEST_FACTORY.construct_url(org_name=target_env.get_dest(),
                                                       artifact_name='sharedflows',
                                                       action='upload',
                                                       param_dict={'sharedflow_name': shared_flow_name})
            response = REQUEST_FACTORY.upload_revision(upload_url, f"{dir_path}/files/{filename}")
            if response.status_code == 201:
                upload_data = response.json()
                response_log_entry['upload'] = upload_data
                target_rev_no = upload_data['revision']
            else:
                raise Exception(f"Shared flow bundle upload unsuccessful: status = {response.status_code}, message = {response.content}")

            # deploy to target env
            # 'https://api.enterprise.apigee.com/v1/organizations/harvard-preprod/environments/stage/sharedflows/adex-dummy-shared-flow/revisions/18/deployments?delay=o&force=true'
            deploy_url = REQUEST_FACTORY.construct_url(org_name=target_env.get_dest(),
                                                       artifact_name='sharedflows',
                                                       action='deploy',
                                                       param_dict={'sharedflow_name': shared_flow_name, 'rev_no': target_rev_no, 'env_name': target_env.get_deploy()})
            response = REQUEST_FACTORY.post(deploy_url)
            if response.status_code == 200:
                response_log_entry['deploy'] = response.json()
            else:
                raise Exception(f"Shared flow revision {target_rev_no} deploy unsuccessful: status = {response.status_code}, message = {response.content}")


            # associate appropriate role with deployed artifact
            role_name = shared_flow_name.split('-')[0] + "-developer"
            assign_role_url = REQUEST_FACTORY.construct_url(org_name=target_env.get_dest(),
                                                            artifact_name='userroles',
                                                            action='assign',
                                                            param_dict={f'{TYPE_MAP["userroles"]}_name': role_name})
            assign_role_body = REQUEST_FACTORY.construct_assign_role_body(artifact_type='sharedflows', artifact_name=shared_flow_name)
 
            response = REQUEST_FACTORY.post(assign_role_url, assign_role_body)
            if response.status_code == 201:
                response_log_entry['assignRole'] = response.json()
            else:
                raise Exception(f"Could not assign role {role_name} to sharedflow {shared_flow_name}: status -> {response.status_code}, message -> {response.content}")
        finally:
            response_log.append({shared_flow_name: response_log_entry})
            # cleanup - remove file(s)
            if os.path.exists(filename):
                os.remove(filename)

    return response_log