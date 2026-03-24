# storage/firebase_manager.py
import firebase_admin
from firebase_admin import credentials, firestore, storage
from datetime import timedelta
import config

class FirebaseManager:
    def __init__(self):
        if not firebase_admin._apps:
            cred = credentials.Certificate(config.FIREBASE_KEY_PATH)
            firebase_admin.initialize_app(cred, {'storageBucket': config.FIREBASE_BUCKET})
        self.db = firestore.client()
        self.bucket = storage.bucket()

    def check_if_processed(self, file_id):
        """Checks the 'Audit Trail' to see if we've ever touched this file."""
        return self.db.collection("processed_images").document(file_id).get().exists

    def upload_and_get_url(self, image_bytes, file_name):
        """Uploads to Storage and returns a 7-day private link."""
        blob = self.bucket.blob(f"vehicles/{file_name}")
        blob.upload_from_string(image_bytes, content_type="image/jpeg")
        return blob.generate_signed_url(expiration=timedelta(days=7))

    def save_detection(self, file_id, vehicle_model):
        """
        SAVES TO TWO PLACES:
        1. 'vehicle_detections' (The Analytics Database)
        2. 'processed_images' (The Audit Trail)
        """
        data = vehicle_model.to_dict()
        
        # Add to the data table
        self.db.collection("vehicle_detections").document(file_id).set(data)
        
        # Log in the audit trail
        self.mark_as_processed(file_id, status="success")

    def mark_as_processed(self, file_id, status="no_vehicle_found"):
        """Logs a file ID in the audit trail so we don't scan it again."""
        self.db.collection("processed_images").document(file_id).set({
            "status": status,
            "timestamp": firestore.SERVER_TIMESTAMP
        })