# using python 3.8.2
import logging
import getpass
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import csv
import requests
import cyberark_identity


########################################################################################################################
main_url = ""
tenant_id = ""
user_name = "" #username of admin user for authentication
csv_username_column_header = "Login Name" # column header for usernames from imported bulkImportUsersTemplate csv
log_filename = "delete_users.log" # name of log file to output to (same folder location as delete_users.py)
########################################################################################################################


# initiate logging
cyberark_identity.initiate_logging(log_filename)


# input user password for authentication
user_password = getpass.getpass(f"Enter the password for {user_name}:\n")

# Create session (session must be created before using identity_api_auth)
token_session = requests.Session()

# authenticate into identity API
cyberark_identity.identity_api_auth(main_url, tenant_id, user_name, user_password, token_session)


# define array of usernames to look up user details for
user_details_array = []

# read in "bulkImportUsersTemplate" csv
print()
print("Please select bulkImportUsersTemplate csv to import from popup file browser:")
Tk().withdraw()
csv_filepath = askopenfilename()
logging.debug("Imported bulkImportUsersTemplate csv path: " + csv_filepath)

with open(csv_filepath, 'r') as f:
    csv_reader = csv.DictReader(f)

    for line in csv_reader:
        csv_username = line[csv_username_column_header]
        user_details_array.append(csv_username)


# define empty user delete array for adding each valid user's username
user_delete_array = []

# Get user details by name (check that each user exists to delete)
for x in user_details_array:
    user_details_url = main_url + "/CDirectoryService/GetUserByName"

    user_details_payload = {"username": x}
    user_details_headers = {
        "accept": "*/*",
        "content-type": "application/json",
        "X-IDAP-NATIVE-CLIENT": "1" # this header is required, otherwise you get 401 error
    }

    user_details_response = token_session.post(user_details_url, json=user_details_payload, headers=user_details_headers)
    user_details_response_json = user_details_response.json()

    # only add user id for users that exist
    if user_details_response_json['success'] == True:
        logging.debug(f"Successfully retrieved the following user: {x}")
        user_delete_array.append(x)

    else:
        logging.debug(f"Unable to retrieve the following user: {x}, unable to delete user")


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
        logging.debug(f"Successfully deleted the following user: {x}")

    else:
        logging.debug(f"Unable to delete the following user: {x}")