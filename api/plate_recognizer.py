# api/plate_recognizer.py
import requests
import json
import time
import config

class PlateRecognizerAPI:
    def __init__(self):
        self.api_key = config.PLATE_REC_API_KEY

    def call_api(self, image_bytes):
        files = {"upload": ("image.jpg", image_bytes, "image/jpeg")}
        data = {
            "config": json.dumps({"detection_mode": "vehicle"}), 
            "mmc": "true", 
            "regions": "de"
        }
        headers = {"Authorization": f"Token {self.api_key}"}
        
        # --- RATE LIMIT PROTECTION ---
        response = requests.post(
            "https://api.platerecognizer.com/v1/plate-reader/",
            data=data, files=files, headers=headers
        )

        # If we hit the 8 calls/sec limit (Status 429)
        if response.status_code == 429:
            print("⚠️ Rate limit hit! Waiting 2 seconds before retry...")
            time.sleep(2)
            return self.call_api(image_bytes) # Recursive retry

        return response.json()