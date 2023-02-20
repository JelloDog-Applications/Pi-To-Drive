import os
import subprocess
import tarfile
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaFileDownload
import argparse

# Define the command line arguments
parser = argparse.ArgumentParser(description='Create a backup of a Raspberry Pi, upload it to Google Drive, or restore data from a backup.')
parser.add_argument('--backup_dir', required=True, help='Path to the directory where the backup file should be stored.')
parser.add_argument('--backup_name', required=True, help='Name of the backup file.')
parser.add_argument('--creds_file', required=True, help='Path to the Google Drive API credentials file.')
parser.add_argument('--backup', action='store_true', help='Create a backup.')
parser.add_argument('--restore', action='store_true', help='Restore data from a backup.')
parser.add_argument('--upload', action='store_true', help='Upload a previously created backup to Google Drive.')
args = parser.parse_args()

# Load the Google Drive API credentials
creds = Credentials.from_authorized_user_file(args.creds_file, ['https://www.googleapis.com/auth/drive'])

if args.backup:
    # Create the backup
    subprocess.call(['sudo', 'tar', '-zcvf', os.path.join(args.backup_dir, args.backup_name), '/'])

    # Upload the backup to Google Drive
    try:
        drive_service = build('drive', 'v3', credentials=creds)
        file_metadata = {'name': 'pi'}
        media = MediaFileUpload(os.path.join(args.backup_dir, args.backup_name), mimetype='application/gzip')
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print('Backup file ID: %s' % file.get('id'))
    except HttpError as error:
        print('An error occurred: %s' % error)
elif args.restore:
    # Download the backup from Google Drive
    try:
        drive_service = build('drive', 'v3', credentials=creds)
        file_id = drive_service.files().list(q="name='" + args.backup_name + "' and trashed = false").execute().get('files')[0].get('id')
        request = drive_service.files().get_media(fileId=file_id)
        fh = MediaFileDownload(os.path.join(args.backup_dir, args.backup_name))
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))
    except HttpError as error:
        print('An error occurred: %s' % error)

    # Restore the backup
    subprocess.call(['sudo', 'tar', '-zxvf', os.path.join(args.backup_dir, args.backup_name), '-C', '/'])
    print('Backup restored.')
elif args.upload:
    # Upload a previously created backup to Google Drive
    try:
        drive_service = build('drive', 'v3', credentials=creds)
        file_metadata = {'name': 'pi'}
        media = MediaFileUpload(os.path.join(args.backup_dir, args.backup_name), mimetype='application/gzip')
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print('Backup file ID: %s' % file.get('id'))
    except HttpError as error:
        print('An error occurred: %s' % error)

