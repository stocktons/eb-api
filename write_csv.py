import csv
from eventbrite_script import make_url, get_data

def write_csv(base_url, parent_cat, parent_cat_id, child_cat, token, header_row, data_row, filepath):
    
    with open(filepath, "w", encoding="utf-8") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(header_row)

            # deal with api pagination  
            while True:
                for item in data:
                    event_data_row = []
                    for element in data_row:
                        event_data_row.append(item[element])
                    csv_writer.writerow(event_data_row)
                    # data_row could look like: 
                    # ['["id"]', '["name"]["text"]', '["start"]["local"]', '["url"]]
                   
                if pagination["has_more_items"] == True:
                    next_page_number = pagination["page_number"] + 1
                    next_page_url = (
                        make_url(base_url, parent_cat, parent_cat_id, child_cat, token, next_page_number)
                    )
                    (data, pagination) = get_data(next_page_url)  
                else:
                    print("no more items!")
                    break