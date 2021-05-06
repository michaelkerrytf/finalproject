from ..env import Env


def migrate_proxies(proxy_list: list, target_env:Env, username:str):
    """
    migrate from source organization to target
    construct response dict

    :param target_env:
    :param proxy_list:
    :return:
    """
    response_log = []
    for proxy in proxy_list: # proxy is an object: {'name': '', 'revision': ''}
        pass
    return response_log
