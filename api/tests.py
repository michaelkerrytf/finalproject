import json

from django.test import TestCase, Client

# Create your tests here.

empty_request_data = {
            "metadata": {
                "ipAddr": "123.123.123.123"
            },
            "request": {
                "sharedFlows": [],
                "proxies": [],
                "specs": [],
                "products": []
            }
        }

class TestResponse(TestCase):

    def test_health(self):
        c = Client()
        response = c.get("/api/health")
        self.assertEqual(response.content, b"{\"message\": \"api is connected to db\"}")

    def test_stage_get(self):
        c = Client()
        response = c.get("/api/migrate/stage")
        self.assertEqual(response.content, b"{\"migrate\": \"stage\"}")

    def test_stage_post_no_body(self):
        c = Client()
        response = c.post("/api/migrate/stage")
        self.assertEqual(response.content, b"{\"message\": \"ERROR: ERROR: Expecting value: line 1 column 1 (char 0)\"}")
        self.assertEqual(response.status_code, 400)

    def test_stage_post_empty_json(self):
        c = Client()
        request_body = {}
        response = c.post("/api/migrate/stage", json.dumps(request_body), content_type="application/json")
        self.assertEqual(response.content, b"{\"message\": \"ERROR: ERROR: \'request\'\"}")
        self.assertEqual(response.status_code, 400)

    def test_stage_post_empty_request_body(self):
        c = Client()
        request_body = {"metadata": {}, "request": {}}
        response = c.post("/api/migrate/stage", json.dumps(request_body), content_type="application/json")
        self.assertEqual(response.content, b"{\"message\": \"ERROR: ERROR: \'tenant-prefix\'\"}")
        self.assertEqual(response.status_code, 400)

    def test_stage_post_empty_artifacts(self):
        c = Client()
        response = c.post("/api/migrate/stage", json.dumps(empty_request_data), content_type="application/json")
        self.assertEqual(response.content,  b'{"message": "ERROR: ERROR: \'tenant-prefix\'"}')
        self.assertEqual(response.status_code, 400)

    def test_prod_get(self):
        c = Client()
        response = c.get("/api/migrate/prod")
        self.assertEqual(response.content, b"{\"migrate\": \"prod\"}")

    def test_prod_post_no_body(self):
        c = Client()
        response = c.post("/api/migrate/prod")
        self.assertEqual(response.content, b"{\"message\": \"ERROR: ERROR: Expecting value: line 1 column 1 (char 0)\"}")
        self.assertEqual(response.status_code, 400)

    def test_prod_post_empty_json(self):
        c = Client()
        request_body = {}
        response = c.post("/api/migrate/prod", json.dumps(request_body), content_type="application/json")
        self.assertEqual(response.content, b"{\"message\": \"ERROR: ERROR: \'request\'\"}")
        self.assertEqual(response.status_code, 400)

    def test_prod_post_empty_request_body(self):
        c = Client()
        request_body = {"metadata": {}, "request": {}}
        response = c.post("/api/migrate/prod", json.dumps(request_body), content_type="application/json")
        self.assertEqual(response.content, b"{\"message\": \"ERROR: ERROR: \'tenant-prefix\'\"}")
        self.assertEqual(response.status_code, 400)

    def test_prod_post_empty_artifacts(self):
        c = Client()
        response = c.post("/api/migrate/prod", json.dumps(empty_request_data), content_type="application/json")
        self.assertEqual(response.content,  b'{"message": "ERROR: ERROR: \'tenant-prefix\'"}')
        self.assertEqual(response.status_code, 400)

    def test_logs_adex_empty(self):
        c = Client()
        response = c.get("/api/migrate/logs/adex")
        content_dict = json.loads(response.content)
        expected = {
            'logs': [],
            'meta': {
                'count': 0,
                'curr': 'http://testserver/api/migrate/logs/adex?offset=0',
                'next': 'http://testserver/api/migrate/logs/adex?offset=0',
                'offset': 0,
                'prev': 'http://testserver/api/migrate/logs/adex?offset=0'
            }
        }

        self.assertEqual(content_dict, expected)
