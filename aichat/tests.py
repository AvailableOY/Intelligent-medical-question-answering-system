import requests

resp = requests.get("http://192.168.6.179:8002/api/v2/heartbeat")
print(resp.json())