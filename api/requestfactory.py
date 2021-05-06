import requests


class RequestFactory:
    """
    RequestFactory handles requests with appropriate authorization
    """
    def __init__(self):
        """
        set up endpoint_info map and other instance variables
        """
        self.base_url = "http://localhost:8000/apigee/organizations/%(org_name)s/"
        self.endpoint_info = {
            "sharedflows": {
                "info": "sharedflows/%(sharedflow_name)s",
                "download": "sharedflows/%(sharedflow_name)s/revisions/%(rev_no)s?format=bundle",
                "upload": "sharedflows?action=import&name=%(sharedflow_name)s",
                "deploy": "environments/%(env_name)s/sharedflows/%(sharedflow_name)s/revisions/%(rev_no)s/deployments?delay=o&force=true",
                "filename": "sharedflow_temp.zip"
            },
            "userroles": {
                "info": "userroles/%(userrole_name)s/users",
                "assign": "userroles/%(userrole_name)s/resourcepermissions"
            }

        }

    def construct_url(self, org_name: str, artifact_name: str, action: str, param_dict: dict = None):
        """
        Constructs a URL appropriate for Apigee Management API based on parameters provided 
        :param org_name: 
        :param artifact_name: 
        :param action: 
        :param param_dict: 
        :return: 
        """
        return self.base_url % {'org_name': org_name} + self.endpoint_info[artifact_name][action] % param_dict

    @staticmethod
    def construct_assign_role_body(artifact_type: str, artifact_name: str):
        return {
            "resourcePermission": [
                {
                    "path": f"/{artifact_type}/{artifact_name}",
                    "permissions": ["delete", "get", "put"]
                },
                {
                    "path": f"/{artifact_type}/{artifact_name}/revisions/*",
                    "permissions": ["delete", "get", "put"]
                },
                {
                    "path": f"/environments/*/{artifact_type}/{artifact_name}/revisions/*/deployments",
                    "permissions": ["delete", "get", "put"]
                }
            ]
        }

    def download(self, url: str) -> requests.Response:
        """
        used to make get requests - could be a json response or file download
        :param url: 
        :return: 
        """
        return requests.get(url)

    def upload_revision(self, url: str, file_name: str = None):
        """
        uploads file to specified URL for Apigee Management API
        :param url: 
        :param file_name: 
        :return: 
        """
        headers = {
            'Content-Type': "multipart/form-data"
        }
        files = {'file': open(file_name, 'rb')}
        return requests.post(url, files=files, headers=headers)

    def post(self, url: str, data: dict = None):
        """
        post data to Apigee Management API, with or without JSON payload
        :param url: 
        :param data: 
        :return: 
        """

        if data:
            headers = {
                'Content-Type': 'application/json'
            }
            return requests.post(url, headers=headers, json=data)
        else:
            return requests.post(url)
