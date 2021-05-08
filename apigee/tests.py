from django.test import TestCase, Client

# Create your tests here.


class MockApigeeTests(TestCase):

    def test_health(self):
        c = Client()
        response = c.get("/api/health")
        self.assertEqual(response.content, b"{\"message\": \"api is connected to db\"}")

