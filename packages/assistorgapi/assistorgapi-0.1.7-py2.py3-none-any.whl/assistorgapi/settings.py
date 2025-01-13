import requests

def get_assist_settings():
    url = "https://assist.org/api/settings"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.text
    else:
        return None