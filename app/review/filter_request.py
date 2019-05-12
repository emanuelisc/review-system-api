import requests
from rest_framework import status
import json


def make_request(title, text):
    payload = {'title': title, 'text': text}
    url = 'http://10.3.0.7:80/'
    headers = {
        'Content-type': 'application/json; charset=utf-8'
    }
    response = requests.request(
        'POST',
        url,
        headers=headers,
        data=json.dumps(payload),
        allow_redirects=False
    )

    if response.status_code == status.HTTP_200_OK:
        # return response.data['results']
        data = response.json()
        return data
    else:
        return {'results': 1, 'probability': 0}
