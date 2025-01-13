import requests

def get_institutions():
    url = "https://assist.org/api/institutions"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.text
    else:
        return None

def get_institutions_academic_years(sendingInstitutionId):
    url = "https://assist.org/api/institutions/"+sendingInstitutionId+"/transferability/availableAcademicYears"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.text
    else:
        return None

def get_institutions_agreements(sendingInstitutionId):
    url = "https://assist.org/api/institutions/"+sendingInstitutionId+"/agreements"
    response = requests.get(url)

    if response.status_code == 200:
        return response.text
    else:
        return None