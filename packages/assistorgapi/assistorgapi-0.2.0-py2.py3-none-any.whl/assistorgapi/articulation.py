import requests

def get_agreements_mod(Key):
    url = "https://assist.org/api/agreements"
    params = {
        "Key": Key
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response
    else:
        return None