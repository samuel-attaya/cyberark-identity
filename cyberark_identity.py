# using python 3.8.2
import sys
import logging


def initiate_logging(filename):
    # main logger config
    logging_level = logging.DEBUG
    logger = logging.getLogger()
    logger.setLevel(level=logging_level)
    logFormatter = logging.Formatter(fmt="%(levelname)s - %(asctime)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S")

    # add logger stream handler
    consoleHandler = logging.StreamHandler(stream=sys.stdout)
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel(level=logging_level)

    logger.addHandler(consoleHandler)

    # add logger file handler
    fileHandler = logging.FileHandler(filename=filename)
    fileHandler.setFormatter(logFormatter)
    fileHandler.setLevel(level=logging_level)

    logger.addHandler(fileHandler)


def identity_api_auth(url, tenant, username, password, session):

    # Start authentication
    auth_url = url + "/Security/StartAuthentication"

    auth_payload = {
        "TenantId": tenant,
        "Version": "1.0",
        "User": username
    }
    auth_headers = {
        "accept": "*/*",
        "content-type": "application/json"
    }

    auth_response = session.post(auth_url, json=auth_payload, headers=auth_headers)
    auth_response_json = auth_response.json()

    logging.info(f"Outcome of start authentication call for {username}: " + str(auth_response_json['success']))
    session_id = auth_response.json()['Result']['SessionId']

    # identify MechanismId for UP (user/pass) auth mechanism (in first challenge)
    first_challenge_mechanism_array = auth_response.json()['Result']['Challenges'][0]['Mechanisms']
    for index, element in enumerate(first_challenge_mechanism_array):
        if element["Name"] == "UP":
            mechanism_id = element['MechanismId']


    # Advance initial authentication
    advance_url = url + "/Security/AdvanceAuthentication"

    advance_payload = {
        "TenantId": tenant,
        "Action": "Answer",
        "SessionId": session_id,
        "PersistentLogin": True,
        "MechanismId": mechanism_id,
        "Answer": password
    }
    advance_headers = {
        "accept": "*/*",
        "content-type": "application/json"
    }

    advance_response = session.post(advance_url, json=advance_payload, headers=advance_headers)
    advance_response_json = advance_response.json()
    logging.info(f"Outcome of advance authentication call for {username}: " + str(advance_response_json['success']))


    # MFA if required for user

    # define answerable vs unanswerable MFA mechanisms
    mfa_answerable = ["EMAIL", "SMS", "OATH", "OTP", "U2F"]
    #mfa_unanswerable = ["PF", "QR"]

    if len(auth_response.json()['Result']['Challenges']) > 1:

        # find all MFA options in second challenge:
        second_challenge_mechanism_options = []
        second_challenge_mechanism_array = auth_response.json()['Result']['Challenges'][1]['Mechanisms']
        for index, element in enumerate(second_challenge_mechanism_array):
            second_challenge_mechanism_options.append(element["Name"])

        # select desired MFA mechanism to use
        print("MFA mechanism options: ")
        print(second_challenge_mechanism_options)
        mfa_mechanism = input("Select MFA mechanism: ")

        for index, element in enumerate(second_challenge_mechanism_array):
            if element["Name"] == mfa_mechanism:
                mfa_mechanism_id = element['MechanismId']


        # MFA Advance authentication
        mfa_advance_url = url + "/Security/AdvanceAuthentication"

        mfa_advance_payload = {
            "TenantId": tenant,
            "Action": "StartOOB",
            "SessionId": session_id,
            "PersistentLogin": True,
            "MechanismId": mfa_mechanism_id
        }
        mfa_advance_headers = {
            "accept": "*/*",
            "content-type": "application/json"
        }

        mfa_advance_response = session.post(mfa_advance_url, json=mfa_advance_payload, headers=mfa_advance_headers)

        mfa_advance_response_json = mfa_advance_response.json()
        logging.info(f"Outcome of MFA advance authentication call for {username}: " + str(mfa_advance_response_json['success']))


        if mfa_mechanism in mfa_answerable:
            mfa_answer = str(input(f"Please input {mfa_mechanism} MFA challenge answer: "))

            mfa_answer_url = url + "/Security/AdvanceAuthentication"

            mfa_answer_payload = {
                "TenantId": tenant,
                "Action": "Answer",
                "SessionId": session_id,
                "PersistentLogin": True,
                "MechanismId": mfa_mechanism_id,
                "Answer": mfa_answer
            }
            mfa_answer_headers = {
                "accept": "*/*",
                "content-type": "application/json"
            }

            mfa_answer_response = session.post(mfa_answer_url, json=mfa_answer_payload, headers=mfa_answer_headers)

            mfa_answer_response_json = mfa_answer_response.json()
            logging.info(f"Outcome of MFA advance answer call for {username}: " + str(
                mfa_answer_response_json['success']))


        # pause script if required to complete unanswerable MFA mechanism
        else:
            input(f"Press 'enter' once {mfa_mechanism} MFA challenge completed")

            # Poll MFA Advance authentication to receive session auth token - polling only required if not answering MFA in script (e.g. clicking auth link in email)
            mfa_poll_url = url + "/Security/AdvanceAuthentication"

            mfa_poll_payload = {
                "TenantId": tenant,
                "Action": "Poll",
                "SessionId": session_id,
                "PersistentLogin": True,
                "MechanismId": mfa_mechanism_id
            }
            mfa_poll_headers = {
                "accept": "*/*",
                "content-type": "application/json"
            }

            mfa_poll_response = session.post(mfa_poll_url, json=mfa_poll_payload, headers=mfa_poll_headers)

            mfa_poll_response_json = mfa_poll_response.json()
            logging.info(f"Outcome of MFA poll call for {username}: " + str(mfa_poll_response_json['success']))

    else:
        logging.info("No MFA required, skipping")


