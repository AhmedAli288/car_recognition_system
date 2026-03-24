# main.py
import time
import config
from api.plate_recognizer import PlateRecognizerAPI
from api.drive_handler import DriveHandler
from storage.firebase_manager import FirebaseManager
from storage.models import VehicleDetection
from firebase_admin import firestore

def run_system():
    drive = DriveHandler()
    api = PlateRecognizerAPI()
    firebase = FirebaseManager()

    print("🚀 Car Recognition System Active (MMC Priority Mode)...")

    while True:
        try:
            files = drive.get_new_files()
            
            for f in files:
                file_id = f['id']
                file_name = f['name']

                if firebase.check_if_processed(file_id):
                    continue

                print(f"📸 Processing: {file_name}")

                try:
                    # 1. DOWNLOAD & ANALYZE
                    img_bytes = drive.download_image(file_id)
                    time.sleep(config.API_RATE_LIMIT_DELAY) # Rate limit protection
                    api_result = api.call_api(img_bytes)

                    # 2. SEARCH ALL RESULTS FOR BEST MMC
                    all_results = api_result.get("results", [])
                    
                    best_vehicle_hit = None
                    highest_mmc_score = -1.0

                    for res in all_results:
                        v_obj = res.get("vehicle")
                        if not v_obj:
                            continue
                        
                        v_props = v_obj.get("props", {})
                        mm_candidates = v_props.get("make_model", [])
                        
                        if mm_candidates:
                            # Sort candidates by score descending
                            sorted_mm = sorted(mm_candidates, key=lambda x: x.get("score", 0), reverse=True)
                            top_guess = sorted_mm[0]
                            current_score = top_guess.get("score", 0.0)

                            # If this vehicle result has a better MMC score than previous ones
                            if current_score > highest_mmc_score:
                                highest_mmc_score = current_score
                                # We store the whole result + the top guess for extraction
                                best_vehicle_hit = {
                                    "full_res": res,
                                    "v_props": v_props,
                                    "best_mm": top_guess
                                }

                    # 3. EXTRACTION (Only if a vehicle was actually found)
                    if best_vehicle_hit:
                        hit = best_vehicle_hit
                        props = hit["v_props"]
                        best_mm = hit["best_mm"]
                        
                        # Safe Extraction for Year (Stored as Integer)
                        year_range = props.get("year", {}).get("year_range", [0, 0])
                        if not isinstance(year_range, (list, tuple)) or len(year_range) < 2:
                            year_range = [0, 0]
                        
                        # Safe Extraction for Color/Orientation
                        colors = props.get("color", [])
                        orients = props.get("orientation", [])
                        
                        best_color = colors[0].get("value", "Unknown") if colors else "Unknown"
                        best_orient = orients[0].get("value", "Unknown") if orients else "Unknown"

                        # Storage & Privacy
                        secure_url = firebase.upload_and_get_url(img_bytes, file_name)
                        
                        # GDPR: Redact plates in the full raw response before saving
                        for r in all_results:
                            if "plate" in r: r["plate"] = "REDACTED"

                        # 4. MAP TO SCHEMA
                        car_data = VehicleDetection(
                            make=best_mm.get("make", "Unknown"),
                            model=best_mm.get("model", "Unknown"),
                            color=best_color,
                            orientation=best_orient,
                            year_start=int(year_range[0]) if year_range[0] else 0,
                            year_end=int(year_range[1]) if year_range[1] else 0,
                            confidence_score=float(highest_mmc_score),
                            image_url=secure_url,
                            drive_file_id=file_id,
                            processed_at=firestore.SERVER_TIMESTAMP,
                            full_api_response=api_result
                        )
                        
                        firebase.save_detection(file_id, car_data)
                        print(f"✅ MMC SUCCESS: {car_data.make} {car_data.model} ({car_data.confidence_score})")

                    else:
                        # TRULY NO VEHICLE FOUND IN ANY RESULT OBJECT
                        firebase.mark_as_processed(file_id, status="no_vehicle_found")
                        print(f"⚠️ No MMC data found in {file_name}. Logged as processed.")

                except Exception as file_error:
                    print(f"❌ Error processing {file_name}: {file_error}")
                    firebase.mark_as_processed(file_id, status=f"error: {str(file_error)[:50]}")
                    continue 

            print(f"Zzz... Sleeping {config.CHECK_INTERVAL}s")
            time.sleep(config.CHECK_INTERVAL)

        except Exception as global_error:
            print(f"❌ Global Error: {global_error}")
            time.sleep(10)

if __name__ == "__main__":
    run_system()