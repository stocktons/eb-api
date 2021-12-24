# class for accessing nested dictionary data with dot notation from
# https://dev.to/taqkarim/extending-simplenamespace-for-nested-dictionaries-58e8

class RecursiveNamespace:

  @staticmethod
  def map_entry(entry):
    if isinstance(entry, dict):
      return RecursiveNamespace(**entry)

    return entry

  def __init__(self, **kwargs):
    for key, val in kwargs.items():
      if type(val) == dict:
        setattr(self, key, RecursiveNamespace(**val))
      elif type(val) == list:
        setattr(self, key, list(map(self.map_entry, val)))
      else:
        setattr(self, key, val)

# my_dict = {
#   "a": {
#     "d": 4,
#   },
#   "b": 2,
#   "c": 3,
#   "e": [5,6,7,{
#     "f": 8,
#   }]
# }

# print(RecursiveNamespace(**my_dict))
# nested = RecursiveNamespace(**my_dict)
# print(getattr(nested, "a"))
# obj = getattr(nested, "a")
# print(getattr(obj, "d"))
# data_row = ["id", ("profile", "name"), ("profile", "email"), 
#         ("profile", "addresses", "home", "country"), ("profile", "addresses", "home", "city"), 
#         "event_id"]
# data =  [{ 
#       "id": "ATTENDEE_ID",
#       "changed": "2021-12-02T04:51:21Z",
#       "created": "2021-12-02T04:51:17Z",
#       "quantity": 1,
#       "variant_id": None,
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
# }]
# for item in data:
#   i = RecursiveNamespace(**item)
#   file_data_row = []
#   for element in data_row:
#       if type(element) is not tuple:
#           e = getattr(i, element, "none")
#           file_data_row.append(e)
#       else:
#           e = getattr(i, element[0], "none")
#           for n in range(1, len(element)):
#             e = getattr(e, element[n], "none")
#           file_data_row.append(e)
            
# print(file_data_row)
