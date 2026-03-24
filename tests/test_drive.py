import firebase_admin
from firebase_admin import credentials, firestore
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- CONFIGURATION ---
# Make sure these names match your files exactly!
DRIVE_KEY = "google_drive_key.json"  
FIREBASE_KEY = "firebase_key.json" 
FOLDER_ID = "1z2R8jp-GPqlBMxd-Pa9SYlY64WZLh40q"

# 1. Connect to Firebase
print("Connecting to Firebase...")
fb_cred = credentials.Certificate(FIREBASE_KEY)
firebase_admin.initialize_app(fb_cred)
db = firestore.client()
print("✅ Firebase Connected!")

# 2. Connect to Google Drive
print("Connecting to Google Drive...")
drive_creds = service_account.Credentials.from_service_account_file(DRIVE_KEY)
drive_service = build('drive', 'v3', credentials=drive_creds)
print("✅ Google Drive Connected!")

# 3. List files in the folder
def check_folder():
    print(f"Checking folder: {FOLDER_ID}")
    query = f"'{FOLDER_ID}' in parents and trashed = false"
    results = drive_service.files().list(q=query).execute()
    files = results.get('files', [])

    if not files:
        print("❌ No files found. Check if you shared the folder with the Service Account email!")
    else:
        print(f"✅ Found {len(files)} files:")
        for f in files:
            print(f"- {f['name']} (ID: {f['id']})")

if __name__ == "__main__":
    check_folder()