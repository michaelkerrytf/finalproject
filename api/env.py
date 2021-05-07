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
            Env.STAGE: {
                "src": "harvard-nonprod",
                "dest": "harvard-preprod",
                "deploy": "stage"
            },
            Env.PROD: {
                "src": "harvard-preprod",
                "dest": "harvard",
                "deploy": "prod"
            }
        }

    def get_src(self):
        return self.get_migration_map()[self]['src']

    def get_dest(self):
        return self.get_migration_map()[self]['dest']
    
    def get_deploy(self):
        return self.get_migration_map()[self]['deploy']
