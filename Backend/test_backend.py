import requests
import json

url = 'http://localhost:5000/search'
data = {'query': 'nitrogen hydrogen'}
headers = {'Content-Type': 'application/json'}

response = requests.post(url, data=json.dumps(data), headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # The response of the POST request
    print(response.json())
else:
    print(f"Request failed with status code {response.status_code}")
