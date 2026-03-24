# test/debug_file.py
import sys
import os
import json

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.drive_handler import DriveHandler
from api.plate_recognizer import PlateRecognizerAPI

def debug_specific_file():
    # 🎯 TARGET FILE INFO
    TARGET_FILE_ID = "11ziwIRid5gdFTRswngSiyM6ycHXsxlsX" # ID for White_ID2427
    TARGET_FILE_NAME = "parked_20260318_170516_White_ID2427.jpg"

    drive = DriveHandler()
    api = PlateRecognizerAPI()

    print(f"--- 🛠 DEBUGGING START: {TARGET_FILE_NAME} ---")
    
    try:
        # 1. Download
        print("📥 Downloading from Drive...")
        img_bytes = drive.download_image(TARGET_FILE_ID)
        
        # 2. Analyze
        print("🧠 Calling Plate Recognizer API...")
        api_result = api.call_api(img_bytes)

        # 3. PRINT RAW RESPONSE (BRUTALLY HONEST)
        print("\n📝 --- RAW API RESPONSE ---")
        print(json.dumps(api_result, indent=4))
        print("---------------------------\n")

        # 4. Analysis Logic
        results = api_result.get("results", [])
        if not results:
            print("❌ ANALYSIS: The API literally found ZERO results (No plate, no car).")
        else:
            res = results[0]
            plate_text = res.get("plate", "None")
            vehicle_obj = res.get("vehicle")
            
            print(f"🔍 Plate Detected: {plate_text}")
            
            if vehicle_obj is None:
                print("❌ ANALYSIS: Plate found, but 'vehicle' is NULL.")
                print("👉 WHY? This usually happens if the car is too close to the camera,")
                print("   the image is cropped too tight around the plate, or the lighting")
                print("   makes the car body look like a 'wall' instead of a vehicle.")
            else:
                print("✅ ANALYSIS: Vehicle object exists.")
                props = vehicle_obj.get("props", {})
                print(f"   Make/Model Score: {props.get('make_model', [{}])[0].get('score', 0)}")

    except Exception as e:
        print(f"💥 CRASH DURING DEBUG: {e}")

if __name__ == "__main__":
    debug_specific_file()