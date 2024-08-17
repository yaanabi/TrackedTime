from win32gui import GetForegroundWindow
import win32process
import psutil
import time
import os
import datetime
import json

from utils import seconds_to_time, time_to_seconds, BASE_PATH

tracked_time_path = os.path.join(BASE_PATH, 'Tracked_Time')

year_dir = os.path.join(tracked_time_path, str(datetime.datetime.now().year))

dir_name = datetime.datetime.today().strftime('%B') + '-' + str(datetime.datetime.today().year)

month_dir = os.path.join(year_dir, dir_name)


def clear():
    """
    Clear console.
    :return: None
    """

    if os.name == 'nt':
        _ = os.system('cls')
    else:

        _ = os.system('clear')


def replace_app_time(app, data, timestamp):
    for item in data:
        if item['app'] == app:
            item['time'] = seconds_to_time(time_to_seconds(item['time']) + int(time.time()) - timestamp[app])


def is_app_in_data(app, data):
    for item in data:
        if item['app'] == app:
            return True
    return False


def create_folders():
    # CREATING BASE DIR
    if not os.path.isdir(tracked_time_path):
        os.mkdir(tracked_time_path)

    # CREATING YEAR DIR
    if not os.path.isdir(year_dir):
        os.mkdir(year_dir)

    # CREATING MONTH DIR
    if not os.path.isdir(month_dir):
        os.mkdir(month_dir)


def get_file_name():
    file_name = f'TrackedTime({datetime.datetime.now().date()}).json'
    return file_name


def get_file_path():
    file_name = get_file_name()
    file_path = f'{month_dir}\\{file_name}'
    return file_path


def get_time_tracker_file(file_path):
    """
    Create json file for time_tracker
    and return json data if file already exist

    :return: None
    """

    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month
    current_day = datetime.datetime.now().day

    json_base_template = {
        'year': current_year,
        'month': current_month,
        'day': current_day,
        'apps': [

        ]
    }

    json_apps_data = []

    if not os.path.isfile(file_path):
        with open(file_path, 'w') as f:
            json.dump(json_base_template, f, indent=4)
    else:
        try:
            with open(file_path, 'r') as f:
                json_data = json.load(f)
                json_apps_data = json_data['apps']
        except Exception as e:
            with open(file_path, 'w') as f:
                json.dump(json_base_template, f, indent=4)
    return json_apps_data


def time_tracker():
    not_track = ['Taskmgr', 'Explorer', 'Conemu64',
                 'Searchui', 'Shellexperiencehost',
                 'Lightshot', 'Steam', 'Applicationframehost',
                 'Steamwebhelper', 'Googledrivesync', 'Signalislandui',
                 'Tracktime', 'Minibin', 'Cmd', 'Lockapp', 'Startmenuexperiencehost',
                 'Pickerhost', ' Zoom_cm_ds_mf8tdjxyt1zsyrvv0dv7wdsk1rgxnsbvbj-8@2mw5xrbllwznevm9_kda7fbb901aef1905',
                 'Openwith', 'Genericsetup', 'Rundll32', 'Firstrun.exe', 'Systemsettingsadminflows', 'Msdt',
                 'Codesetupstabledddecbaecdddfdtmp',
                 'Easeofaccessdialog', 'Codesetup-stable-622cb03f7e070a9670c94bae1a45d78d7181fbd4.tmp']
    # Create base folders
    create_folders()

    # Clear console
    clear()

    #
    file_path = get_file_path()

    # Get json apps data file
    json_apps_data = get_time_tracker_file(file_path)

    timestamp = {}

    # Start time tracking
    while True:
        try:
            current_app = psutil.Process(
                abs(win32process.GetWindowThreadProcessId(GetForegroundWindow())[1])).name().replace('.exe',
                                                                                                     '').capitalize()
            if current_app in not_track:
                time.sleep(1)  # Without sleep caused an error
                continue
            timestamp[current_app] = int(time.time())

            time.sleep(1)

            if not is_app_in_data(current_app, json_apps_data):
                json_apps_data.append({'app': current_app, 'time': '00:00:00'})

            replace_app_time(current_app, json_apps_data, timestamp)

            clear()

            json_apps_data = sorted(json_apps_data, key=lambda val: time_to_seconds(val['time']), reverse=True)

            for item in json_apps_data:
                print('| %s: %-35s |' % (item['time'], item['app']))
            with open(file_path, 'r') as f:
                new_json = json.load(f)
                new_json['apps'] = json_apps_data
            with open(file_path, 'w') as f:
                json.dump(new_json, f, indent=4)

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            time.sleep(1)
            pass
