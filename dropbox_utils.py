import dropbox
import logging

logger = logging.getLogger(__name__)

class DropboxUtils:
    def __init__(self, token: str) -> None:
        try:
            logger.info('Connecting to Dropbox')
            self.dbx = dropbox.Dropbox(token)
        except Exception as e:
            logger.exception(f'Failed to connect to Dropbox: {str(e)}')

    def dropbox_upload(self, file_path: str, dbx_path: str):
        """
        Upload a file to Dropbox.
        :param file_path: str
        :param dbx_path: str
        :return: None
        """
        try:
            logger.info(f'Uploading file {file_path} to Dropbox')
            with open(file_path, 'rb') as f:
                self.dbx.files_upload(f.read(), dbx_path, mode=dropbox.files.WriteMode.overwrite)
        except Exception as e:
            logger.exception(f'Failed to upload file {file_path} to Dropbox: {str(e)}')

    def get_dropbox_content(self, file_path: str) -> str:
        """
        Download file to dropbox
        :param file_path: str
        :return: str
        """
        content = self.dbx.files_download(file_path)[1].content
        return content

# def dropbox_connect(token: str):
#     """
#     Connect to dropbox
#     :param token: str
#     :return: dropbox.dropbox_client.Dropbox
#     """

#     try:
#         dbx = dropbox.Dropbox(token)
#     except dropbox.exceptions.AuthError as e:
#         print('Error connecting to Dropbox with access token: ', str(e))
#     return dbx


# def dropbox_upload(dbx: dropbox.dropbox_client.Dropbox, file_path: str, dbx_path: str):
#     """
#     Upload file to dropbox
#     :param dbx: dropbox.dropbox_client.Dropbox
#     :param file_path: str
#     :param dbx_path: str
#     :return: None
#     """

#     with open(file_path, 'rb') as f:
#         dbx.files_upload(f.read(), dbx_path, mode=dropbox.files.WriteMode.overwrite)


# def get_dropbox_content(dbx: dropbox.dropbox_client.Dropbox, file_path: str) -> str:
#     """
#     Download file to dropbox
#     :param dbx: dropbox.dropbox_client.Dropbox
#     :param file_path: str
#     :return: str
#     """
#     content = dbx.files_download(file_path)[1].content
#     return content
