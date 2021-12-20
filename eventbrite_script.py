import csv
import json
import requests
import os


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
# basic pagination url:
# f"{BASE_URL}{parent_cat}/{parent_cat_id}/{child_cat}/?page={next_page_number}&token={token}"

TOKEN = os.environ.get("EB_TOKEN")
ORG_ID = os.environ.get("ORG_ID")
BASE_URL = "https://www.eventbriteapi.com/v3/"

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

def get_all_events():
    parent_cat = "organizations"
    child_cat = "events"
    api_events_url = make_url(BASE_URL, parent_cat, ORG_ID, child_cat, TOKEN)
    api_response = requests.get(api_events_url)
    api_response_text = json.loads(api_response.text)

    # api_response_text looks like: 
    # {
    #   "pagination": {
    #      "object_count": 321,
    #      "page_number": 1,
    #      "page_size": 50,
    #      "page_count": 7,
    #      "continuation": "cOnTinUaTionC0d3",
    #      "has_more_items": true
    #    },
    #   "events": [
    #       {
    #         "name": {
    #           "text": "Event Name Goes Here!",
    #             ...
    #          },
    #          ...
    #          "url": "https://www.eventbrite.com/e/event-name-goes-here-123456789",
    #          "id": "123456789",
    #          "start": {
    #             "timezone": "America/Los_Angeles",
    #             "local": "20212-01-01T18:30:00",
    #             "utc": "2022-01-01T01:30:00Z",
    #           },
    #           ...
    #       },
    #       ...
    #     ]
    #  }

    events = api_response_text.get("events")
    pagination = api_response_text.get("pagination")

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

def get_event_attendees(base_url, parent_cat, parent_cat_id, child_cat, token):
    print("getting event attendees")
    api_attendees_url = (
        f"{base_url}{parent_cat}/{parent_cat_id}/{child_cat}/?token={token}"
    )
    api_response = requests.get(api_attendees_url)
    api_response_text = json.loads(api_response.text)

# api_response looks like:
# {
#   "pagination": {
#     "object_count": 65,
#     "page_number": 1,
#     "page_size": 50,
#     "page_count": 2,
#     "continuation": "cOnTinUaTionC0d3",
#     "has_more_items": true
#   },
#   "attendees": [
#     {
#       ...
#       },
#       "resource_uri": "https://www.eventbriteapi.com/v3/events/EVENT_ID/
#           attendees/ATTENDEE_ID/",
#       "id": "ATTENDEE_ID",
#       "changed": "2021-12-02T04:51:21Z",
#       "created": "2021-12-02T04:51:17Z",
#       "quantity": 1,
#       "variant_id": null,
#       "profile": {
#         "first_name": "First",
#         "last_name": "Last",
#         "email": "first_last@emailadress.com",
#         "name": "First Last",
#         "addresses": {
#           "home": {
#             "city": "San Francisco",
#             "country": "US",
#             "region": "CA",
#             "postal_code": "91409",
#             "address_1": "1234 Street Ave",
#             "address_2": "Unit 42"
#           }
#         },
#       },
#       "event_id": "EVENT_ID",
#  ...
#   ]
# }

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
                # The Eventbrite docs indicate that the following should work to get
                # to the next page, and it does in Insomnia, but not in this script:
                # next_page_url = (api_url + "?continuation=" + 
                #     pagination["continuation"])
                # In this script, that pattern returns a 401 error code.
                #
                # Instead, follow this pattern to make the next url to access:
                # (https://www.eventbriteapi.com/v3/events/EVENT_ID/attendees/
                #   ?page=2&token=TOKEN)

                next_page_number = pagination["page_number"] + 1
                next_page_url = (
                    f"{base_url}{parent_cat}/{parent_cat_id}/{child_cat}/"
                    f"?page={next_page_number}&token={token}"
                )
                next_page_response = requests.get(next_page_url)
                next_page_response_text = json.loads(next_page_response.text)
                attendees = next_page_response_text.get("attendees")
                pagination = next_page_response_text.get("pagination")
            else:
                print("no more attendees!")
                break

def get_all_attendees():
    # there is an endpoint for this.
    pass

def get_api_data():
    pass

def get_paginated_api_data():
    pass

get_all_events()
# get_event_attendees(BASE_URL, "events", "27492994286", "attendees", TOKEN)

