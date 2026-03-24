import io
import json
import requests
import firebase_admin
from firebase_admin import credentials, firestore, storage
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from datetime import timedelta

# --- CONFIGURATION ---
DRIVE_KEY = "google_drive_key.json"
FIREBASE_KEY = "firebase_key.json"
# ⬇️ PASTE YOUR ACTUAL PLATE RECOGNIZER API KEY HERE
API_KEY = "c095bb8fa7bbccced6c2baf5d086e525a8b632de" 
FOLDER_ID = "1z2R8jp-GPqlBMxd-Pa9SYlY64WZLh40q"
# ⬇️ THIS IS THE BUCKET YOU JUST FOUND
STORAGE_BUCKET = "vehicle-make-data.firebasestorage.app" 

# 1. Initialize Everything
if not firebase_admin._apps:
    fb_cred = credentials.Certificate(FIREBASE_KEY)
    firebase_admin.initialize_app(fb_cred, {'storageBucket': STORAGE_BUCKET})

db = firestore.client()
bucket = storage.bucket()

drive_creds = service_account.Credentials.from_service_account_file(DRIVE_KEY)
drive_service = build('drive', 'v3', credentials=drive_creds)

def run_single_test():
    # A. Find the first image from your list
    print("Checking Google Drive...")
    results = drive_service.files().list(q=f"'{FOLDER_ID}' in parents", pageSize=1).execute()
    items = results.get('files', [])
    
    if not items:
        print("No files found in Drive.")
        return
    
    file_id = items[0]['id']
    file_name = items[0]['name']
    print(f"Reading file: {file_name}")

    # B. Download file into memory
    request = drive_service.files().get_media(fileId=file_id)
    file_stream = io.BytesIO()
    downloader = MediaIoBaseDownload(file_stream, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    
    file_stream.seek(0)
    image_bytes = file_stream.read()

    # C. Send to Plate Recognizer API
    print("Sending to Plate Recognizer API...")
    # Resetting the pointer for the upload
    files = {"upload": ("image.jpg", image_bytes, "image/jpeg")}
    data = {
        "config": json.dumps({"detection_mode": "vehicle"}), 
        "mmc": "true", 
        "regions": "de"
    }
    headers = {"Authorization": f"Token {API_KEY}"}
    
    response = requests.post(
        "https://api.platerecognizer.com/v1/plate-reader/",
        data=data,
        files=files,
        headers=headers
    )
    api_data = response.json()

    # D. Upload to Firebase Storage
    print("Uploading image to Firebase Storage...")
    blob = bucket.blob(f"test_detections/{file_name}")
    blob.upload_from_string(image_bytes, content_type="image/jpeg")
    
    # Generate a secure link that expires in 7 days
    image_url = blob.generate_signed_url(expiration=timedelta(days=7))

    # E. Save to Firestore
# E. Save to Firestore
    print("Saving metadata to Firestore...")
    if api_data.get("results"):
        res = api_data["results"][0]
        v_props = res.get("vehicle", {}).get("props", {})
        
        # --- NEW: PRIVACY CLEANUP (Optional for GDPR) ---
        # If the API found a plate, we wipe the text so we don't store PII
        for result in api_data.get("results", []):
            if "plate" in result:
                result["plate"] = "REDACTED" # Hide the actual numbers

        # --- PREPARE DATA ---
        mm_candidates = v_props.get("make_model", [])
        best_mm = mm_candidates[0] if mm_candidates else {}
        
        year_range = v_props.get("year", {}).get("year_range")
        year_str = f"{year_range[0]}-{year_range[1]}" if year_range else "Unknown"

        final_data = {
            "make": best_mm.get("make", "Unknown"),
            "model": best_mm.get("model", "Unknown"),
            "year": year_str,
            "color": v_props.get("color", [{}])[0].get("value", "Unknown"),
            "orientation": v_props.get("orientation", [{}])[0].get("value", "Unknown"),
            "direction": res.get("direction"),
            "image_url": image_url,
            
            # 🔥 THIS IS THE CHANGE: Saving the WHOLE response
            "full_api_response": api_data, 
            
            "timestamp": firestore.SERVER_TIMESTAMP
        }

        db.collection("vehicle_detections").add(final_data)
        print("-" * 30)
        print(f"✅ SUCCESS! Full record saved for {file_name}")
        print("-" * 30)
    else:
        print("❌ API did not detect a vehicle in this image.")

if __name__ == "__main__":
    run_single_test()