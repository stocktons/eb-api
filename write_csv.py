import csv
import requests
import json
import os

from requests.api import get
from RecursiveNamespace import RecursiveNamespace

TOKEN = os.environ.get("EB_TOKEN")
ORG_ID = os.environ.get("ORG_ID")
BASE_URL = "https://www.eventbriteapi.com/v3/"

def make_url(parent_cat, parent_cat_id, child_cat):
    return f"{BASE_URL}{parent_cat}/{parent_cat_id}/{child_cat}/?token={TOKEN}"

def modify_url(url, next_page_number):
    (main, token) = url.split("?")
    return f"{main}?page={next_page_number}&{token}"

def get_data(api_url, child_cat):
    api_response = requests.get(api_url)
    api_response_text = json.loads(api_response.text)
    # see sample_api_responses.txt to see a sample of some of the data returned
    data = api_response_text.get(child_cat)
    pagination = api_response_text.get("pagination")
    return data, pagination

def write_csv(url, child_cat, header_row, data_row, filepath):
    """Takes in user's choice for csv column names, aka the 
    -- header_row, which could look like: ["id", "name", "date", "url"], the
    -- data_row, which is a list of keys from the returned api data that the 
       user would like to pull the values from. A data_row could look like: 
       ["id", ("name", "text"), ("start", "local"), "url"], where you want to 
       grab the values of id, text, local, and url for the csv. Tuples indicate 
       nested objects in the API output. 
    -- url is the api endpoint with token, and 
    -- filepath is the destination file path for the new csv.
    """
    
    (data, pagination) = get_data(url, child_cat)
    with open(filepath, "w", encoding="utf-8") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(header_row)

            while True:
                for item in data:
                    i = RecursiveNamespace(**item)
                    file_data_row = []
                    for element in data_row:
                        if type(element) is not tuple:
                            e = getattr(i, element, "none")
                            file_data_row.append(e)
                        else:
                            # access the first nested dictionary
                            e = getattr(i, element[0], "none")
                            # walk through the nested data to the end to find
                            # the value of the last key in our data_row element
                            for n in range(1, len(element)):
                                e = getattr(e, element[n], "none")
                            file_data_row.append(e)
                             
                    csv_writer.writerow(file_data_row)
                   
                # deal with api pagination  
                if pagination["has_more_items"]:
                    next_page_number = pagination["page_number"] + 1
                    next_page_url = (
                        modify_url(url, next_page_number)
                    )
                    (data, pagination) = get_data(next_page_url, child_cat)
                    print(f"...fetching page {next_page_number}")  
                else:
                    print("no more items!")
                    break

def api_to_csv(url_params, header_row, data_row, filepath):
    url = make_url(*url_params)
    write_csv(url, url_params[2], header_row, data_row, filepath)


# # get all attendees
# api_to_csv(
#     ["organizations", ORG_ID, "attendees"],
#     ["id", "name", "email", "country", "city", "event_id"], 
#     ["id", ("profile", "name"), ("profile", "email"), 
#         ("profile", "addresses", "home", "country"), ("profile", "addresses", "home", "city"), 
#         "event_id"], 
#     "./csv_files/attendees.csv",
# )

## get all events
# api_to_csv(
#     ["organizations", ORG_ID, "events"],
#     ["id", "name", "date", "url"], 
#     ["id", ("name", "text"), ("start", "local"), "url"], 
#     "./csv_files/events.csv",
# )

## get attendees of one event
api_to_csv(
    ["events", "123456789", "attendees"],
    ["id", "name", "email", "country", "city"], 
    ["id", ("profile", "name"), ("profile", "email"), ("profile", "addresses", "home", "country"), ("profile", "addresses", "home", "city")], 
    "./csv_files/event-123456789-attendees.csv",
)