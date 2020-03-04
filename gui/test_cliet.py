import http.client

SERVER_ENDPOINT = "my-json-server.typicode.com/KevinDaLam/json-test/db"
http_client = http.client.HTTPSConnection(SERVER_ENDPOINT)
http_client.request("GET", "")

response = self.parent().http_client.getresponse()
print("Status: {} and reason: {}".format(response.status, response.reason))
print(response.read().decode())