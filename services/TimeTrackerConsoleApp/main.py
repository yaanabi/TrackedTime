from apscheduler.schedulers.background import BackgroundScheduler

import logging
import trackTime
import requests
import keyring
import datetime
import json
from dotenv import load_dotenv
import os
import sys
import re

load_dotenv()
DBX_TOKEN = os.getenv('DBX_TOKEN')


def check_token_expiration(jwt: str, jwt_refresh: str) -> tuple[bool, str]:
    """
    Check if the given JWT token is valid, if not try to refresh the
    token and return the new one.

    Args:
        jwt (str): The JWT token
        jwt_refresh (str): The refresh token

    Returns:
        tuple[bool, str]: A tuple containing a boolean indicating if the
        token is valid and the new token if it is.
    """
    payload = {"token": jwt}
    r = requests.post(
        "http://127.0.0.1:8000/auth/api/token/verify/", data=payload)
    if r.status_code == 200:
        logger.info(f"{r.status_code} JWT Token valid")
        return (True, jwt)
    else:
        logger.error(
            f"{r.status_code} JWT Token invalid. Trying to refresh jwt")
        payload = {"refresh": jwt_refresh}
        r = requests.post(
            "http://127.0.0.1:8000/auth/api/token/refresh/", data=payload)
        if r.status_code == 200:
            logger.info(
                f"{r.status_code} JWT Refresh Token valid, returning new JWT")
            return (True, r.json()['access'])
        else:
            logger.error(f"{r.status_code} JWT Refresh Token invalid")
            return (False, None)


def validate_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if (re.fullmatch(regex, email)) and len(email) <= 255:
        return True
    return False


def validate_username(username):
    """
    Validates a username using regular expressions.
    Alphanumeric characters, underscores, and hyphens
    Minimum length of 3 characters
    Maximum length of 30 characters
    Args:
        username (str): The username to validate.

    Returns:
        bool: True if the username is valid, False otherwise.
    """
    # Define the regular expression pattern for username validation
    username_pattern = r"^[a-zA-Z0-9_-]{3,30}$"

    # Check if the username matches the pattern
    if re.match(username_pattern, username):
        return True
    else:
        return False


def validate_password(password):
    """
    Validates a password using regular expressions.
    At least one letter
    At least one digit
    At least one special character (e.g. @, $, !, %, *, #, ?, &)
    Minimum length of 8 characters

    Args:
        password (str): The password to validate.

    Returns:
        bool: True if the password is valid, False otherwise.
    """
    # Define the regular expression pattern for password validation
    password_pattern = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"

    # Check if the password matches the pattern
    if re.match(password_pattern, password):
        return True
    else:
        return False


def register():

    username = input("Enter your username: ")

    while not validate_username(username):
        print("Username not valid\n")
        print("Your password should contain:\nAlphanumeric characters, underscores, and hyphens\nMinimum length of 3 characters\nMaximum length of 30 characters")
        username = input("Enter your username: ")

    password1 = input("Enter your password: ")

    while not validate_password(password1):
        print("Password not valid\n")
        print("Your password should contain:\nAt least one letter\nAt least one digit\nAt least one special character (e.g. @, $, !, %, *, #, ?, &)\nMinimum length of 8 characters")
        password1 = input("Enter your password: ")

    password2 = input("Enter your password again: ")

    while password1 != password2:
        print("Passwords do not match")
        password2 = input("Enter your password again: ")

    email = input("Enter your email: ")

    while not validate_email(email):
        print("Email not valid\n")
        email = input("Enter your email: ")

    payload = {
        "username": username,
        "password1": password1,
        "password2": password2,
        "email": email
    }
    url = 'http://127.0.0.1:8000/auth/api/register/'

    r = requests.post(url, data=payload)

    if r.status_code == 201:
        print("Registration successful, please login\n")
        login()
    else:
        print(f"Registration failed, status code {r.status_code}({r.reason}), please try again\n")
        resp_data = json.loads(r.text)
        for source, reason in resp_data.items():
            reasons = ' '.join(reason)
            print(f"{source}: {reasons}")
        register()


def login():
    try:
        while True:
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            payload = {
                "username": username,
                "password": password
            }
            # Post the credentials to the token endpoint
            r = requests.post(
                "http://127.0.0.1:8000/auth/api/token/", data=payload)
            if r.status_code == 200:
                # If the credentials are valid, get the jwt and refresh token
                jwt = (r.json()).get('access')
                jwt_refresh = (r.json()).get('refresh')
                # Save the jwt and refresh token to keyring
                keyring.set_password('time_tracker', 'jwt', jwt)
                keyring.set_password(
                    'time_tracker', 'jwt_refresh', jwt_refresh)
                logger.info('Added jwt and refresh token to keyring')
                # Break out of the loop
                break
            elif r.status_code == 401:
                # If the credentials are invalid, print an error message
                print("Invalid username or password")
            else:
                # If there is another error, print the status code
                print("Something went wrong, status code:", r.status_code)
    except KeyboardInterrupt:
        # If the user presses Ctrl+C, exit the program
        print("Exiting program")
        sys.exit(0)


def get_today_tracked_time_id(jwt):
    year, month, day = datetime.datetime.now(
    ).year, datetime.datetime.now().month, datetime.datetime.now().day
    url = 'http://127.0.0.1:8000/api/trackedtime/'
    query = {
        'year': year,
        'month': month,
        'day': day
    }
    headers = {
        'Authorization': f'Bearer {jwt}'
    }
    r = requests.get(url=url, params=query, headers=headers)
    if r.json():
        tracked_time_id = r.json()[0]["id"]
        return tracked_time_id
    else:
        return None


def set_jwt_token(jwt, jwt_refresh):
    """
    Check if jwt is valid, if not prompt user for login and
    save the new jwt and refresh token to keyring.

    Args:
        jwt (str): The JWT token
        jwt_refresh (str): The refresh token

    Returns:
        jwt (str): The JWT token
        jwt_refresh (str): The refresh token
    """
    is_jwtvalid, jwt = check_token_expiration(jwt, jwt_refresh)
    if not is_jwtvalid:
        # If the jwt is invalid, prompt user for login
        login()
    else:
        # If the jwt is valid, save it to keyring
        keyring.set_password('time_tracker', 'jwt', jwt)
    # Get the jwt and refresh token from keyring
    jwt, jwt_refresh = keyring.get_password(
        'time_tracker', 'jwt'), keyring.get_password('time_tracker', 'jwt_refresh')
    return jwt, jwt_refresh


def authenticate():
    choice = input(
        'If you want to login, type 1. If you want to register, press 2: ')
    if choice.replace(' ', '').strip() == '1':
        login()
    elif choice.replace(' ', '').strip() == '2':
        register()
    else:
        print('Invalid choice')
        return authenticate()


def upload_to_db():
    """
    This function is used as a close handler for the time tracker.
    It uploads the current time tracking data to the DB
    """
    try:
        # Get the file path and name of the current time tracking data
        file_path = trackTime.get_file_path()
        apps = trackTime.get_time_tracker_data(file_path)
        jwt = keyring.get_password('time_tracker', 'jwt')
        jwt_refresh = keyring.get_password('time_tracker', 'jwt_refresh')
        jwt = set_jwt_token(jwt, jwt_refresh)[0]

        tracked_time_id = get_today_tracked_time_id(jwt)
        if tracked_time_id is None:
            logger.info(
                'No tracked time found for today, creating new tracked time')
            url = 'http://127.0.0.1:8000/api/trackedtime/'
            headers = {
                'Authorization': f'Bearer {jwt}'
            }
            r = requests.post(url=url, headers=headers, json={'apps': apps})
            if r.status_code < 300:
                logger.info(
                    'Tracked Time was created, status code: ' + str(r.status_code))
            else:
                logger.error(
                    'Tracked Time was not created, status code: ' + str(r.status_code))
        else:
            url = f'http://127.0.0.1:8000/api/trackedtime/{tracked_time_id}/'
            headers = {
                'Authorization': f'Bearer {jwt}'
            }
            r = requests.patch(url=url, headers=headers, json=apps)
            logger.info(
                'Tracked Time was updated, status code: ' + str(r.status_code))
    except Exception as e:
        logger.error(e)
        print(e)


def main():
    try:
        logger.info('Tracker started')
        jwt_refresh = keyring.get_password('time_tracker', 'jwt_refresh')
        if jwt_refresh is None:
            authenticate()
        else:
            choice = input(
                'If you want to logout type 1, otherwise press any key: ')
            if choice.replace(' ', '').strip() == '1':
                authenticate()
        scheduler = BackgroundScheduler()  # Create a background scheduler

        # Add a job to the scheduler to run the close handler every hour
        scheduler.add_job(upload_to_db, 'interval', minutes=20)
        scheduler.start()  # Start the scheduler

        trackTime.time_tracker()  # Start the time tracker

    except KeyboardInterrupt:  # Catch the KeyboardInterrupt exception when the user stops the script
        upload_to_db()  # Call the close handler to upload the file to Dropbox
        print("Exiting program, sending data to db...")
    except Exception as e:
        logger.error(e)
        print(e)


if __name__ == '__main__':
    # Configure logger
    logging.basicConfig(filename=os.path.join(os.path.dirname(__file__), 'tracker.log'), encoding='utf-8',
                        format='[%(asctime)s] [%(filename)s:%(lineno)d] [%(levelname)s] - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG)

    # Create logger
    logger = logging.getLogger(__name__)

    main()

# DO TESTING
