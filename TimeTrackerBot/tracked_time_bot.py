import dropbox
import datetime
import telebot
import json
import os
from collections import defaultdict
import sys 

# Import errors for exception handling
from dropbox.exceptions import ApiError
from dropbox.files import DownloadError

# sys.path.append('C:\\Users\\nabiu\\Projects\\petprojects\\TimeTracker')

from dropbox_utils import DropboxUtils
from utils import seconds_to_time, time_to_seconds, BASE_PATH, get_bot_message

from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
DBX_TOKEN = os.getenv('DBX_TOKEN')

class TelegramBot:

    def __init__(self, token: str):
        self.bot = telebot.TeleBot(token)
        self.dbx = DropboxUtils(DBX_TOKEN)
        self.dbx_path = '/App Tracker/Tracked_Time/'
        self.register_handlers()
    
    def register_handlers(self):
        self.bot.add_message_handler(self.send_day_data, commands=['day'])
        self.bot.add_message_handler(self.send_month_data, commands=['month'])
        self.bot.add_message_handler(self.send_today_data, commands=['today'])


    def send_day_data(self, message):
        """
        Send tracked time of the day that user entered.
        Message format: "/day YYYY:MM:DD"
        """
        try:
            # Extract the date from the message
            date = message.text[4:].strip()

            # Construct the file name with the date
            file_name = 'TrackedTime({}).json'.format(date)

            # Get the content of the file from Dropbox
            dbx_file = self.dbx.get_dropbox_content(self.dbx_path + file_name)

            # Parse the JSON content
            dbx_json = json.loads(dbx_file)

            # Get the bot message from the JSON data
            bot_message = get_bot_message(dbx_json)

            # Send the bot message to the user
            self.bot.send_message(message.chat.id, bot_message)

        except Exception as ex:
            # If an exception occurs, get the error message and send it to the user
            error_message = self.get_error_message(ex)
            self.bot.send_message(message.chat.id, error_message)


    def send_month_data(self, message):
        """
        Send current month tracked time.

        Parameters
        ----------
        message : telebot.types.Message
            The message object received from the user.
        """
        try:
            # Get the current month and year and construct the directory name
            dir_name = datetime.datetime.today().strftime('%B') + '-' + str(datetime.datetime.today().year)
            
            # Initialize a dictionary to store the tracked time for each app
            month_data = defaultdict(lambda: 0)
            
            # Construct the directory path
            dir_path = os.path.join(BASE_PATH, '.\\Tracked_Time', str(datetime.datetime.today().year), dir_name)
            
            # Get the list of files in the directory
            dir_list = os.listdir(dir_path)
            
            # Iterate over each file in the directory
            for file in dir_list:
                file_path = os.path.join(dir_path, file)
                
                # Read the JSON content of the file
                with open(file_path) as json_file:
                    data = json.load(json_file)
                
                # Iterate over each entry in the 'apps' list
                for el in data['apps']:
                    # Add the tracked time for the app to the dictionary
                    month_data[el['app']] += time_to_seconds(el['time'])
            
            # Sort the dictionary by the tracked time in seconds
            sorted_data = sorted(month_data.items(), key=lambda el: el[1], reverse=True)
            
            # Create a new dictionary with the sorted data
            month_data = dict(sorted_data)
            
            # Construct the bot message with the tracked time for each app
            bot_message = ''
            for k, v in month_data.items():
                bot_message += f'|{k} -- {seconds_to_time(v)}\n'
            
            # Send the bot message to the user
            self.bot.send_message(message.chat.id, bot_message)
        except Exception as ex:
            # If an exception occurs, get the error message and send it to the user
            error_message = self.get_error_message(ex)
            self.bot.send_message(message.chat.id, error_message)


    def send_today_data(self, message):
        """
        Send today's tracked time.

        Parameters
        ----------
        message : telebot.types.Message
            The message object received from the user.

        Returns
        -------
        None
        """
        try:
            # Construct the file name with the current date
            file_name = 'TrackedTime({}).json'.format(datetime.datetime.now().date())

            # Get the content of the file from Dropbox
            dbx_file = self.dbx.get_dropbox_content(self.dbx_path + file_name)

            # Parse the JSON content
            dbx_json = json.loads(dbx_file)

            # Get the bot message from the JSON data
            bot_message = get_bot_message(dbx_json)

            # Send the bot message to the user
            self.bot.send_message(message.chat.id, bot_message)

        except Exception as ex:
            # If an exception occurs, get the error message and send it to the user
            error_message = self.get_error_message(ex)
            self.bot.send_message(message.chat.id, error_message)

    def run(self):
        self.bot.polling()

    def get_error_message(self, ex):
        """
        Get error message from given exception.

        Parameters
        ----------
        ex : Exception
            The exception to get the error message from.

        Returns
        -------
        str
            The error message.
        """
        error_message = 'Unexpected Error'
        if isinstance(ex, ApiError):
            # If error is a dropbox error
            if isinstance(ex.error, DownloadError):
                # If error is a download error
                error = ex.error.get_path()
                if error.is_not_found():
                    # File not found
                    error_message = 'Download Error: File not found'
                elif error.is_malformed_path():
                    # Malformed path
                    error_message = 'Download Error: Malformed path'
                elif error.is_not_file():
                    # Given path refers to something that isn't a file
                    error_message = 'Download Error: Given path refers to something that isn\'t a file'
                elif error.is_not_folder():
                    # Given path refers to something that isn't a folder
                    error_message = 'Download Error: Give path refers to something that isn\'t a folder'
                elif error.is_restricted_content():
                    # Content is restricted
                    error_message = 'Download Error: Content is restricted'
                elif error.is_other():
                    # Other error
                    error_message = 'Download Error: Other error'
            else:
                # Other dropbox error
                error_message = 'Dropbox Error: {}'.format(ex.error)
        else:
            # Other error
            error_message = f'Error: {ex}'
        return error_message




if __name__ == '__main__':
    bot = TelegramBot(BOT_TOKEN)
    bot.run()