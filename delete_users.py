# using python 3.8.2
import logging
import getpass
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import csv
import requests
import cyberark_identity


########################################################################################################################
main_url = "https://example.id.cyberark.cloud"
tenant_id = "example"
user_name = "user@domain" # username of admin user for authentication
csv_username_column_header = "Login Name" # column header for usernames from imported bulkImportUsersTemplate.csv
log_filename = "delete_users.log" # name of log file to output to (output to same folder location as delete_users.py)
########################################################################################################################


# initiate logging
cyberark_identity.initiate_logging(log_filename)


# input user password for authentication
user_password = getpass.getpass(f"Enter the password for {user_name}:\n")

# Create session (session must be created before using identity_api_auth)
token_session = requests.Session()

# authenticate into identity API
cyberark_identity.identity_api_auth(main_url, tenant_id, user_name, user_password, token_session)


# define array of usernames to validate that username exists in Identity tenant
user_validate_array = []

# read in "bulkImportUsersTemplate" csv
print()
print("Please select bulkImportUsersTemplate csv to import from popup file browser:")
Tk().withdraw()
csv_filepath = askopenfilename()
logging.info("Imported bulkImportUsersTemplate csv path: " + csv_filepath)

with open(csv_filepath, 'r') as f:
    csv_reader = csv.DictReader(f)

    for line in csv_reader:
        csv_username = line[csv_username_column_header]
        user_validate_array.append(csv_username)


# return list of all tenant usernames (up to 100,000 users returned inquery)
user_list_url = main_url + "/RedRock/query"

user_list_payload = {
    "Script": "@@All Users",
    "Args": {
        "PageNumber":1,
        "PageSize":100000,
        "Limit":100000,
        "SortBy":"Username",
        "Ascending":True,
        "Direction":"ASC",
        "Caching":-1
    }
}
user_list_headers = {
    "accept": "*/*",
    "content-type": "application/json",
    "X-IDAP-NATIVE-CLIENT": "1" # this header is required, otherwise you get 401 error
}

user_list_response = token_session.post(user_list_url, json=user_list_payload, headers=user_list_headers)
user_list_response_json = user_list_response.json()
user_list_objects = user_list_response_json['Result']['Results']

user_list_username_array = []

for x in user_list_objects:
    object_username = x['Row']['Username']
    user_list_username_array.append(object_username)


# define empty user delete array for all valid usernames
user_delete_array = []

# validate all usernames imported from csv against API user list for tenant
for x in user_validate_array:
    if x in user_list_username_array:
        logging.info(f"Successfully retrieved the following user: {x}")
        user_delete_array.append(x)

    else:
        logging.info(f"Unable to retrieve the following user: {x}, unable to delete user")


# Delete all users in user_delete_array
for x in user_delete_array:
    user_delete_url = main_url + "/UserMgmt/RemoveUser?ID=" + x

    user_delete_headers = {
        "accept": "*/*",
        "content-type": "application/json",
        "X-IDAP-NATIVE-CLIENT": "1"
    }

    user_delete_response = token_session.post(user_delete_url, headers=user_delete_headers)
    user_delete_response_json = user_delete_response.json()

    if user_delete_response_json['success'] == True:
        logging.info(f"Successfully deleted the following user: {x}")

    else:
        logging.debug(f"Unable to delete the following user: {x}")