import json
import unittest
import server

class ApiTests(unittest.TestCase):
    def test_health(self):
        status, _, body = server.handle("GET", "/health", {})
        self.assertEqual(status, 200)
        self.assertTrue(json.loads(body)["ok"])

    def test_unknown_route(self):
        self.assertEqual(server.handle("GET", "/missing", {})[0], 404)

    def test_validation(self):
        status, _, body = server.handle("POST", "/diff", {})
        self.assertEqual(status, 400)

if __name__ == "__main__":
    unittest.main()
