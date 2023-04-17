import os
import tempfile
import dropbox
import pathlib
import pandas as pd
from dropbox.exceptions import AuthError
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
# import os
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# # Set the access token as an environment variable
# access_token = os.environ['DROPBOX_ACCESS_TOKEN']

def _dropbox_connect(access_token):
    """Create a connection to Dropbox."""

    try:
        dbx = dropbox.Dropbox(access_token)
    except AuthError as e:
        print('Error connecting to Dropbox with access token: ' + str(e))
    return dbx



def dropbox_list_files(access_token, path):
    """Return a Pandas dataframe of files in a given Dropbox folder path in the Apps directory.
    """

    dbx = _dropbox_connect(access_token)

    try:
        files = dbx.files_list_folder(path).entries
        files_list = []
        for file in files:
            if isinstance(file, dropbox.files.FileMetadata):
                metadata = {
                    'name': file.name,
                    'path_display': file.path_display,
                    'client_modified': file.client_modified,
                    'server_modified': file.server_modified
                }
                files_list.append(metadata)

        df = pd.DataFrame.from_records(files_list)
        print(df.name)
        return df.sort_values(by='server_modified', ascending=False)

    except Exception as e:
        print('Error getting list of files from Dropbox: ' + str(e))


def dropbox_download_file(access_token, dropbox_file_path, local_file_path):
    """Download a file from Dropbox to the local machine."""

    try:
        dbx = _dropbox_connect(access_token)

        with open(local_file_path, 'wb') as f:
            metadata, result = dbx.files_download(path=dropbox_file_path)
            f.write(result.content)
    except Exception as e:
        print('Error downloading file from Dropbox: ' + str(e))


def dropbox_upload_file(access_token, local_path, local_file, dropbox_file_path):
    """Upload a file from the local machine to a path in the Dropbox app directory.

    Args:
        local_path (str): The path to the local file.
        local_file (str): The name of the local file.
        dropbox_file_path (str): The path to the file in the Dropbox app directory.

    Example:
        dropbox_upload_file('.', 'test.csv', '/stuff/test.csv')

    Returns:
        meta: The Dropbox file metadata.
    """

    try:
        dbx = _dropbox_connect(access_token)

        local_file_path = pathlib.Path(local_path) / local_file

        with local_file_path.open("rb") as f:
            meta = dbx.files_upload(f.read(), dropbox_file_path, mode=dropbox.files.WriteMode("overwrite"))

            return meta
    except Exception as e:
        print('Error uploading file to Dropbox: ' + str(e))



def dropbox_get_link(access_token, dropbox_file_path):
    """Get a shared link for a Dropbox file path.

    Args:
        dropbox_file_path (str): The path to the file in the Dropbox app directory.

    Returns:
        link: The shared link.
    """

    try:
        dbx = _dropbox_connect(access_token)
        shared_link_metadata = dbx.sharing_create_shared_link_with_settings(dropbox_file_path)
        shared_link = shared_link_metadata.url
        return shared_link.replace('?dl=0', '?dl=1')
    except dropbox.exceptions.ApiError as exception:
        if exception.error.is_shared_link_already_exists():
            shared_link_metadata = dbx.sharing_get_shared_links(dropbox_file_path)
            shared_link = shared_link_metadata.links[0].url
            return shared_link.replace('?dl=0', '?dl=1')


if __name__ == '__main__':

    # dropbox_list_files(access_token, '/templates')
    # download = dropbox_download_file(access_token, "/templates/closing.mp4", "download.mp4")
    # upload = dropbox_upload_file(access_token, '.', 'upload.mp4', '/output/upload.mp4')
    # link = dropbox_get_link(access_token, '/output/upload.mp4')
    print("Do something")

