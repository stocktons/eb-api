import csv
import json
import requests
import os
import write_csv
import get_data


# Get all events belonging to an organization:
# "https://www.eventbriteapi.com/v3/organizations/ORG_ID/events/?token=TOKEN"
# Results come back 50 per page, if more than 50 results, use pagination url for further calls:
# "https://www.eventbriteapi.com/v3/organizations/ORG_ID/events/?page=2&token=TOKEN"
#
# Get all attendees of every event:
# "https://www.eventbriteapi.com/v3/organizations/ORG_ID/attendees/?token=TOKEN"
# Results come back 50 per page, if more than 50 results, use pagination url:
# "https://www.eventbriteapi.com/v3/organizations/ORG_ID/attendees/?page=2&token=TOKEN"
#
# Get all attendees of a certain event:
# "https://www.eventbriteapi.com/v3/events/EVENT_ID/attendees/?token=TOKEN"
# Results come back 50 per page, if more than 50 results, use pagination url:
# "https://www.eventbriteapi.com/v3/events/EVENT_ID/attendees/?page=2&token=TOKEN"
#
# basic Eventbrite API url format:
# f"{BASE_URL}{parent_cat}/{parent_cat_id}/{child_cat}/?token={token}"
#
# basic pagination url format:
# f"{BASE_URL}{parent_cat}/{parent_cat_id}/{child_cat}/?page={next_page_number}&token={token}"

TOKEN = os.environ.get("EB_TOKEN")
ORG_ID = os.environ.get("ORG_ID")
BASE_URL = "https://www.eventbriteapi.com/v3/"

# HELPER FUNCTIONS
def make_url(base_url, parent_cat, parent_cat_id, child_cat, token, next_page_number=None):
    if not next_page_number:
        return f"{base_url}{parent_cat}/{parent_cat_id}/{child_cat}/?token={token}"
    else:
        return (
            f"{base_url}{parent_cat}/{parent_cat_id}/{child_cat}/"
            f"?page={next_page_number}&token={token}"
        )

def get_next_page(pagination, parent_cat, parent_cat_id, child_cat):
    # The Eventbrite docs indicate that the following should work to get
    # to the next page, and it does in Insomnia, but not in this script:
    # next_page_url = (api_events_url + "?continuation=" + 
    #     pagination["continuation"])
    # In this script, that pattern returns a 401 error code.
    #
    # Instead, follow this pattern to make the next url to access:
    # (https://www.eventbriteapi.com/v3/organizations/ORG_ID/
    #     events/?page=2&token=TOKEN)
    next_page_number = pagination["page_number"] + 1
    next_page_url = (
        make_url(BASE_URL, parent_cat, parent_cat_id, child_cat, TOKEN, next_page_number)
    )
    next_page_response = requests.get(next_page_url)
    next_page_response_text = json.loads(next_page_response.text)
    events = next_page_response_text.get("events")
    pagination = next_page_response_text.get("pagination")
    return events, pagination

# API CALLS
def get_all(base_url, parent_cat, parent_cat_id, child_cat, token):
    """Get all the events belonging to an organization, output selected data into csv"""

    api_url = make_url(base_url, parent_cat, parent_cat_id, child_cat, token)
    (data, pagination) = get_data(api_url)
    # see sample_api_responses.txt to see a sample of some of the data returned

    with open("./csv_files/all_events.csv", "w", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([
            "id",
            "name",
            "date",
            "url",
        ])

        # deal with api pagination  
        while True:
            for event in events:
                event_data_row = [
                    event["id"],
                    event["name"]["text"],
                    event["start"]["local"],
                    event["url"],
                ]
                csv_writer.writerow(event_data_row)
        
            if pagination["has_more_items"] == True:
                (events, pagination) = (
                    get_next_page(pagination, parent_cat, ORG_ID, child_cat)
                )     
            else:
                print("no more events!")
                break

def get_event_attendees(parent_cat, parent_cat_id, child_cat):
    """Get all the attendees of one event and output selected data into csv."""

    api_attendees_url = make_url(
        BASE_URL, parent_cat, parent_cat_id, child_cat, TOKEN
        )
    api_response = requests.get(api_attendees_url)
    api_response_text = json.loads(api_response.text)
    # see sample_api_responses.txt to see a sample of some of the data returned

    attendees = api_response_text.get("attendees")
    pagination = api_response_text.get("pagination")

    with open(
        f"./csv_files/event_{parent_cat_id}_attendees.csv", "w", encoding="utf-8"
        ) as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([
            "attendee_id",
            "first_name",
            "last_name",
            "name",
            "email",
            "event_id",
        ])

    # deal with api pagination  
        while True:
            for attendee in attendees:
                attendee_data_row = [
                    attendee["id"],
                    attendee["profile"]["first_name"],
                    attendee["profile"]["last_name"],
                    attendee["profile"]["name"],
                    attendee["profile"]["email"],
                    attendee["event_id"],
                ]
                csv_writer.writerow(attendee_data_row)
        
            if pagination["has_more_items"] == True:
                (attendees, pagination) = (
                    get_next_page(pagination, parent_cat, ORG_ID, child_cat)
                )     
            else:
                print("no more attendees!")
                break

def get_all_attendees():
    # there is an endpoint for this.
    pass

# def get_api_data():
#     pass

# def get_paginated_api_data():
#     pass

# get_all_events()
# get_event_attendees("events", "27492994286", "attendees")


