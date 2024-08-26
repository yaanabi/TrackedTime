from apscheduler.schedulers.background import BackgroundScheduler

import logging
import trackTime
# import dropbox_utils
import dropbox_utils

from dotenv import load_dotenv
import os

load_dotenv()
DBX_TOKEN = os.getenv('DBX_TOKEN')

# Configure logger
logging.basicConfig(filename='./tracker.log', encoding='utf-8', 
                    format='[%(asctime)s] [%(filename)s:%(lineno)d] [%(levelname)s] - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG)

# Create logger
logger = logging.getLogger(__name__)


def close_handler():
    """
    This function is used as a close handler for the time tracker.
    It uploads the current time tracking data to the Dropbox.
    """
    # Connect to Dropbox
    dbx = dropbox_utils.DropboxUtils(DBX_TOKEN)

    # Get the file path and name of the current time tracking data
    file_path = trackTime.get_file_path()
    file_name = trackTime.get_file_name()

    # Construct the Dropbox path
    dbx_path = '/App Tracker/Tracked_Time/' + file_name

    # UPLOAD JSON FILE TO DROPBOX
    dbx.dropbox_upload(file_path, dbx_path)

    # Log the successful upload
    logger.info('Json file was uploaded to Dropbox')


def main():
    try:
        logger.info('Tracker started') 
        scheduler = BackgroundScheduler()  # Create a background scheduler
        # Add a job to the scheduler to run the close handler every hour
        scheduler.add_job(close_handler, 'interval', hours=1)
        scheduler.start()  # Start the scheduler
        trackTime.time_tracker()  # Start the time tracker

    except KeyboardInterrupt:  # Catch the KeyboardInterrupt exception when the user stops the script
        close_handler()  # Call the close handler to upload the file to Dropbox

if __name__ == '__main__':
    main()