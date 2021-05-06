from enum import Enum


class Env(Enum):
    """
    Environment enum containing information about the associated apigee organizations
    """
    DEV = "dev"
    STAGE = "stage"
    PROD = "prod"

    @staticmethod
    def get_migration_map():
        return {
            "stage": {
                "src": "harvard-nonprod",
                "dest": "harvard-preprod",
                "deploy": "stage"
            },
            "prod": {
                "src": "harvard-preprod",
                "dest": "harvard",
                "deploy": "prod"
            }
        }

    def get_src(self):
        return self.get_migration_map()[self.value]['src']

    def get_dest(self):
        return self.get_migration_map()[self.value]['dest']
    
    def get_deploy(self):
        return self.get_migration_map()[self.value]['deploy']
