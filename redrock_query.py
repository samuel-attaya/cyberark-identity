# using python 3.8.2
import logging
import getpass
import requests
import cyberark_identity


########################################################################################################################
main_url = "https://example.id.cyberark.cloud"
tenant_id = "example"
user_name = "user@domain" # username of admin user for authentication
log_filename = "delete_users.log" # name of log file to output to (output to same folder location as delete_users.py)
specified_role_name = "test role"
########################################################################################################################


# initiate logging
cyberark_identity.initiate_logging(log_filename)


# input user password for authentication
user_password = getpass.getpass(f"Enter the password for {user_name}:\n")

# Create session (session must be created before using identity_api_auth)
token_session = requests.Session()

# authenticate into identity API
cyberark_identity.identity_api_auth(main_url, tenant_id, user_name, user_password, token_session)


# return list of all tenant web applications (up to 100,000 apps returned in query)
application_list_url = main_url + "/RedRock/query"

application_list_payload = {
    "Script": "@@Web Applications PLV8",
    "Args": {
        "PageNumber":1,
        "PageSize":100000,
        "Limit":100000,
        "SortBy":"Name",
        "Ascending":True,
        "Direction":"ASC",
        "Caching":-1
    }
}

application_list_headers = {
    "accept": "*/*",
    "content-type": "application/json",
    "X-IDAP-NATIVE-CLIENT": "1" # this header is required, otherwise you get 401 error
}

application_list_response = token_session.post(application_list_url, json=application_list_payload, headers=application_list_headers)
application_list_response_json = application_list_response.json()
application_list_objects = application_list_response_json['Result']['Results']

web_app_id_list = []

for x in application_list_objects:
    web_app_id = x['Row']['ID']
    web_app_id_list.append(web_app_id)


final_role_app_list = []

#do API call for each web app to get permissions
for x in web_app_id_list:
    permission_url = main_url + "/Acl/GetRowAces"

    permission_payload = {
        "ReduceSysadmin": True,
        "RowKey": x,
        "Table": "Application",
        "Args": {
            "PageNumber": 1,
            "PageSize": 100000,
            "Limit": 100000,
            "SortBy": "",
            "Caching": -1
        }
    }
    permission_headers = {
        "accept": "*/*",
        "content-type": "application/json",
        "X-IDAP-NATIVE-CLIENT": "1"  # this header is required, otherwise you get 401 error
    }

    permission_response = token_session.post(permission_url, json=permission_payload, headers=permission_headers)
    permission_response_json = permission_response.json()
    for row in permission_response_json['Result']:
        if row['PrincipalType'] == "Role" and row['PrincipalName'] == specified_role_name:
            final_app = "App ID:", x, "Role:", row['PrincipalName']
            final_role_app_list.append(final_app)

#return all apps that have permission row for role in question
for x in final_role_app_list:
    print(x)


