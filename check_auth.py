
import requests

url = 'http://localhost:8000/api/auth/login'
data = {'username': 'test@test.com', 'password': 'password'}
resp = requests.post(url, data=data)
print(resp.status_code, resp.text)

