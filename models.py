import requests
from dotenv import dotenv_values

config = dotenv_values(".env")
apiUrl = config["API_URL"]

payload = {}
headers = {}
response = requests.request("GET", apiUrl + 'models', headers=headers, data=payload)

print(response.text)
