import requests
import json

def get_data(api_url):
    api_response = requests.get(api_url)
    api_response_text = json.loads(api_response.text)
    # see sample_api_responses.txt to see a sample of some of the data returned
    
    data = api_response_text.get("child_cat")
    pagination = api_response_text.get("pagination")

    return data, pagination