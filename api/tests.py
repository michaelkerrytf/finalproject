import json

from django.test import TestCase, Client

# Create your tests here.


class TestResponse(TestCase):

    def test_health(self):
        c = Client()
        response = c.get("/health/")
        self.assertEqual(response.content, b"{\"message\": \"application is connected to db\"}")

    def test_stage_get(self):
        c = Client()
        response = c.get("/migrate/stage/")
        self.assertEqual(response.content, b"{\"migrate\": \"stage\"}")

    def test_stage_post_no_body(self):
        c = Client()
        response = c.post("/migrate/stage/")
        self.assertEqual(response.content, b"{\"message\": \"ERROR: ERROR: Expecting value: line 1 column 1 (char 0)\"}")
        self.assertEqual(response.status_code, 400)

    def test_stage_post_empty_json(self):
        c = Client()
        request_body = {}
        response = c.post("/migrate/stage/", json.dumps(request_body), content_type="application/json")
        self.assertEqual(response.content, b"{\"message\": \"ERROR: \'request\'\"}")
        self.assertEqual(response.status_code, 500)

    def test_stage_post_empty_request_body(self):
        c = Client()
        request_body = {"metadata":{}, "request":{}}
        response = c.post("/migrate/stage/", json.dumps(request_body), content_type="application/json")
        self.assertEqual(response.content, b"{\"message\": \"ERROR: \'sharedFlows\'\"}")
        self.assertEqual(response.status_code, 500)

    def test_stage_post_empty_artifacts(self):
        request_data = {
            "metadata": {
                "ipAddr": "123.123.123.123"
            },
            "request":{
                "sharedFlows":[],
                "proxies":[],
                "specs":[],
                "products":[]
            }
        }

        c = Client()
        response = c.post("/migrate/stage/", json.dumps(request_data), content_type="application/json")
        self.assertEqual(response.content, b"{\"sharedFlows\": [], \"proxies\": [], \"specs\": [], \"products\": []}")
        self.assertEqual(response.status_code, 200)

    def test_prod_get(self):
        c = Client()
        response = c.get("/migrate/prod/")
        self.assertEqual(response.content, b"{\"migrate\": \"prod\"}")

    # def test_logs_adex(self):
    #     c = Client()
    #     response = c.get("/migrate/logs/adex")
    #     content_dict = json.load(response.content)
    #     self.assertEqual(content_dict, {})
