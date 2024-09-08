from win32gui import GetForegroundWindow
import win32process
import psutil
import time
import os
import datetime
import json
import logging
import utils

logger = logging.getLogger(__name__)

tracked_time_path = os.path.join(utils.BASE_PATH, 'TrackedTime')

year_dir = os.path.join(tracked_time_path, str(datetime.datetime.now().year))

dir_name = datetime.datetime.today().strftime(
    '%B') + '-' + str(datetime.datetime.today().year)

month_dir = os.path.join(year_dir, dir_name)


def clear():
    """
    Clear console.
    :return: None
    """
    _ = os.system('cls')


def create_folders():
    # CREATING BASE DIR
    """
    Create directories for saving tracked time data, if they do not exist yet.

    Creates the following directories if they do not exist yet:
        - {BASE_PATH}/TrackedTime
        - {BASE_PATH}/TrackedTime/{current_year}
        - {BASE_PATH}/TrackedTime/{current_year}/{current_month}-{current_year}

    :return: None
    """
    if not os.path.isdir(tracked_time_path):
        os.mkdir(tracked_time_path)

    # CREATING YEAR DIR
    if not os.path.isdir(year_dir):
        os.mkdir(year_dir)

    # CREATING MONTH DIR
    if not os.path.isdir(month_dir):
        os.mkdir(month_dir)


def get_file_name():
    """
    Returns the name of the file for the current day.

    The file name is in the format 'TrackedTime({date}).json'.

    :return: The name of the file for the current day.
    """
    file_name = f'TrackedTime({datetime.datetime.now().date()}).json'
    return file_name


def get_file_path():
    """
    Returns the path of the file for the current day.

    The file name is in the format 'TrackedTime({date}).json' and is located in the directory
    for the current month.

    :return: The path of the file for the current day.
    """
    # Get the name of the file for the current day.
    file_name = get_file_name()

    # Construct the full path of the file.
    file_path = os.path.join(month_dir, file_name)

    return file_path


def get_time_tracker_data(file_path):
    """
    Creates a new JSON file for time tracking at the specified path if it doesn't already exist.
    If the file already exists, it loads the existing data from the file.

    :param file_path: The path of the file to create or load.
    :return: The existing time tracking data from the file, or an empty dictionary if the file is new.
    """
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month
    current_day = datetime.datetime.now().day

    # The base structure of the JSON file.
    json_base_template = {
        'year': current_year,
        'month': current_month,
        'day': current_day,
        'apps': {}  # The app data is stored here.
    }

    json_apps_data = dict()

    if not os.path.isfile(file_path):
        # Create the file if it doesn't exist.
        with open(file_path, 'w') as f:
            json.dump(json_base_template, f, indent=4)
    else:
        try:
            # Load the existing data from the file.
            with open(file_path, 'r') as f:
                json_data = json.load(f)
                json_apps_data = json_data['apps']
        except Exception as e:
            # If there is an error loading the data, overwrite it with a new one.
            with open(file_path, 'w') as f:
                json.dump(json_base_template, f, indent=4)
    return json_apps_data


def time_tracker():
    """
    Main time tracking function. This function will continuously run until stopped.

    It will track the time of the current foreground window and store it in a JSON file.
    The JSON file will contain the time tracked for each app, sorted by the most time tracked.
    """
    # Exclude these apps from tracking
    not_track = [
        'Taskmgr', 'Explorer', 'Conemu64',
        'Searchui', 'Shellexperiencehost',
        'Lightshot', 'Steam', 'Applicationframehost',
        'Steamwebhelper', 'Googledrivesync', 'Signalislandui',
        'Tracktime', 'Minibin', 'Cmd', 'Lockapp', 'Startmenuexperiencehost',
        'Pickerhost', ' Zoom_cm_ds_mf8tdjxyt1zsyrvv0dv7wdsk1rgxnsbvbj-8@2mw5xrbllwznevm9_kda7fbb901aef1905',
        'Openwith', 'Genericsetup', 'Rundll32', 'Firstrun.exe', 'Systemsettingsadminflows', 'Msdt',
        'Codesetupstabledddecbaecdddfdtmp',
        'Easeofaccessdialog', 'Codesetup-stable-622cb03f7e070a9670c94bae1a45d78d7181fbd4.tmp'
    ]

    # Create base folders if they don't exist
    create_folders()

    # Clear console
    clear()
    print('Welcome to Time Tracker!')
    
    # Get the path of the JSON file
    file_path = get_file_path()

    # Get the existing data from the JSON file
    json_apps_data = get_time_tracker_data(file_path)

    # Create a dictionary to store the timestamps of the apps
    timestamp = {}

    # Start time tracking
    while True:
        try:
            # Get the current foreground window
            current_app = psutil.Process(
                abs(win32process.GetWindowThreadProcessId(GetForegroundWindow())[1])).name().replace('.exe', '').capitalize()

            # If the app is in the exclude list, skip it
            if current_app in not_track:
                # time.sleep(1)  # Without sleep caused an error
                continue

            # Set the timestamp of the app to the current time
            timestamp[current_app] = int(time.time())

            # Sleep for 1 second before checking again
            time.sleep(1)

            # Update the time of the app in the data
            json_apps_data.update({current_app: utils.seconds_to_time(
                utils.time_to_seconds(json_apps_data.get(current_app, '00:00:00')) + int(time.time()) - timestamp[current_app])})

            # Clear the console and print the updated data
            clear()

            json_apps_data = dict(sorted(json_apps_data.items(
            ), key=lambda x: utils.time_to_seconds(x[1]), reverse=True))
            for app, apptime in json_apps_data.items():
                print('| %s: %-35s |' % (apptime, app))

            # Write the updated data to the JSON file
            with open(file_path, 'r') as f:
                new_json = json.load(f)
                new_json['apps'] = json_apps_data
            with open(file_path, 'w') as f:
                json.dump(new_json, f, indent=4)

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # If the process doesn't exist, or we don't have access to it, or it's a zombie process, skip it
            time.sleep(1)
            pass

        except Exception as e:
            if e != KeyboardInterrupt:
                logger.exception(f'Failed to track time: {str(e)}')

