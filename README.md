# cyberark-identity

The purpose of this repository is to house all scripts created to assist in the administration of the CyberArk Identity platform.

## contents of repository:
- requirements.txt - list of all python library dependencies for this repository
- cyberark_identity.py - includes general functions used by all scripts in this repository
- delete_users.py - deletes users from a specified CyberArk Identity tenant based on an imported bulkImportUsersTemplate.csv
- bulkImportUsersTemplate.csv - blank version of the CyberArk Identity standard user import template for use with scripts

## prerequisites to run scripts:
- this repository cloned or downloaded to your local machine
- python 3.8.2
- all python libraries listed in requirements.txt (to install all libraries navigate to the cyberark-identity repository folder in the terminal and run "pip install -r requirements.txt")
- credentials for a CyberArk Identity admin user from your tenant that has the ability to run API calls
- the tenant url and tenant id for the CyberArk Identity tenant that you are looking to update

## directions for script use:
### - delete_users.py
  1. Navigate to the "cyberark-identity" repository folder on your machine.
  2. Open delete_user.py and enter values for the main_url, tenant_id, and user_name variables at the top of the script. Save the file.
  3. Navigate to the cyberark-identity folder in the terminal and run "python delete_users.py".
  4. Follow the instructions in the terminal to type in your user password, then press enter. (NOTE: password input is masked, so no characters will display in the terminal)
  5. If user requires MFA, follow these steps (otherwise skip to step vi.):
     1. From the "MFA mechanism options" specified in the terminal, type in the desired mechanism and press enter.
     2. MFA will now be initiated. Complete MFA mechanism and press enter in the terminal once this has been completed.
  6. From the file browser that opens, select the bulkImportUsersTemplate that has the list of users that you wish to delete and click open. (WARNING: only import csv with users you wish to delete, as all users in csv will be deleted)
  7. Output from user search/delete operations will display in the terminal, as well as the log file defined by the log_filename variable in delete_users.py (default value is delete_users.log).

