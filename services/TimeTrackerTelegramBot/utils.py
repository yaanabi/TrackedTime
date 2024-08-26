import os
BASE_PATH = os.path.dirname(os.path.abspath(__file__))


def time_to_seconds(time: str) -> int:
    """
    Get seconds from time.
    Time format is hh:mm:ss

    :param time: str
    :return: int
    """
    h, m, s = time.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)


def seconds_to_time(seconds: int) -> str:
    """
    Convert second to the readable format of time.

    :param seconds: int
    :return: str
    """
    return '{:02}:{:02}:{:02}'.format(seconds // 3600, seconds % 3600 // 60, seconds % 3600 % 60)


def get_bot_message(dbx_json) -> str:
    """
    Get formatted bot message with dropbox json data
    :param dbx_json: dict
    :return: str
    """
    bot_message = ''
    for el in dbx_json['apps']:
        bot_message += f'App: {el["app"]}\n'
        bot_message += f'Time spent: {el["time"]}\n\n'
    return bot_message