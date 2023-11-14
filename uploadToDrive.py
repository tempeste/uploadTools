# python script_name.py --source /path/to/source/directory --folder_id <folderId> --extension jpg
# Folder Id is the string after folders/ in the drive url: https://drive.google.com/drive/folders/1b1JwZYPZBNSPwVcBBqF6PKJzasnGl4hS
import os
import glob
import shutil
import argparse
import tempfile
from PIL import Image
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Function to strip metadata and rename the image
def process_image(input_path, counter):
    with Image.open(input_path) as img:
        # Create a temporary file for the processed image
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(input_path)[1])
        img.save(temp_file.name)
    return temp_file.name, f"{counter:03d}{os.path.splitext(input_path)[1]}"

# Function to upload file to Google Drive
def upload_to_drive(service, file_name, file_path, folder_id=None):
    file_metadata = {'name': file_name}
    if folder_id:
        file_metadata['parents'] = [folder_id]
    
    # Determine the MIME type based on the file extension
    mime_type = "image/jpeg"  # default
    if file_name.lower().endswith('.png'):
        mime_type = "image/png"
    elif file_name.lower().endswith('.gif'):
        mime_type = "image/gif"
    # Add other formats as needed

    media = MediaFileUpload(file_path, mimetype=mime_type)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"File ID: {file.get('id')}")

# Set up argument parsing
parser = argparse.ArgumentParser(description='Process and upload images to Google Drive.')
parser.add_argument('--source', required=True, help='Source directory containing images')
parser.add_argument('--folder_id', help='Google Drive folder ID to upload images')
parser.add_argument('--extension', required=True, help='Image file extension (e.g., png, jpg)')
parser.add_argument('--offset', type=int, default=0, help='Offset for image numbering') # If you want to start from 3, then offset=3

# Parse arguments
args = parser.parse_args()

# Google Drive API setup
SCOPES = ['https://www.googleapis.com/auth/drive']
creds = None
# Load or create credentials here (see Google Drive API documentation for details)
# The file token.json stores the user's access and refresh tokens
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        # An out-of-band url used for cli
        # flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')
                
        # Same thing, also for an out-of-band method, but with a different redirect URI, in this case, the authorization code can be found as part of the url params instead of a proper webpage
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES, redirect_uri='http://127.0.0.1:8080')
        # If running on a local machine with a browser, use the following line:
        # creds = flow.run_local_server(port=0)
        
        # Otherwise, if running in a container/ headless environment, use the following lines instead:
        auth_url, _ = flow.authorization_url(prompt='consent')

        print("Please go to this URL and authorize access:")
        print(auth_url)  # User needs to visit this URL

        code = input("Enter the authorization code: ")
        flow.fetch_token(code=code)
        creds = flow.credentials
        
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

service = build('drive', 'v3', credentials=creds)

# Process images and upload
counter = args.offset
for image_file in glob.glob(os.path.join(args.source, '*' + args.extension)):
    temp_file_path, processed_name = process_image(image_file, counter)
    upload_to_drive(service, processed_name, temp_file_path, args.folder_id)
    os.remove(temp_file_path)  # Delete the temporary file after upload
    counter += 1

print("Image processing and uploading complete.")
