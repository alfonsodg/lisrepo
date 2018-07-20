import requests
import json

url = 'http://localhost:8888/api/v1/patient/142552'
headers = {'X-Api-Key': '5954032458e83fc75abf23afd1c01ce2'}

r = requests.get(url, headers=headers)

data = json.loads(r.text)
print(data)