from .requestfactory import RequestFactory

# TYPE_MAP is used to translate singular values into plurals
TYPE_MAP = {
    "sharedflows": "sharedflow",
    "proxies": "proxy",
    "products": "product",
    "specs": "spec",
    "userroles": "userrole"
}

ARTIFACTS_WITH_REVISIONS = ['sharedflows', 'proxies']
REQUEST_KEYS_NO_ARTIFACTS = ['buildTags', 'comment']

REQUEST_FACTORY = RequestFactory()
