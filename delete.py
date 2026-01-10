
import requests


for i in range(1001):
    print(i)
    
    response = requests.request(url="https://github.com/mohitkumhar", method="GET")


# print(response.content)
