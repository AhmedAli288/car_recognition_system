# 🚗 Car Recognition System (Make & Model Detection + Firebase Storage)

## 📌 Overview

This project is a **backend pipeline** that processes car images, extracts vehicle information (make, model, etc.), and stores the results in **Firebase (Firestore + Storage)**.

The system uses the **Plate Recognizer API in vehicle mode** to infer car details without relying on visible license plates.

---

## 🎯 Features

* 🔍 Detect **car make & model**
* 🎨 Extract **color, orientation, year range**
* 📊 Store **multiple prediction candidates**
* ☁️ Upload images to **Firebase Storage**
* 🗄️ Save structured metadata to **Firestore**
* 🔒 Privacy-safe (license plates are removed)
* 🔁 Automatically processes new images from Google Drive

---

## 🧠 System Architecture

```text
Google Drive Image
        ↓
Download Image
        ↓
Plate Recognizer API (vehicle mode)
        ↓
Extract vehicle metadata
        ↓
Upload image → Firebase Storage
        ↓
Save metadata → Firestore
```

---

## ⚙️ Technologies Used

* Python
* Plate Recognizer
* Firebase:

  * Firestore (database)
  * Storage (image hosting)
* Google Drive API

---

## 📦 Project Structure

```text
project/
├── main.py
├── config.py
├── api/
│   ├── plate_recognizer.py
│   └── drive_handler.py
├── utils/
│   └── extractor.py
├── storage/
│   ├── firebase_manager.py
│   └── models.py
├── utils/
│   └── helpers.py
├── keys/
│   ├── firebase_key.json
│   └── google_drive_key.json
├── requirements.txt
```

---

## 🔌 API Configuration

The system uses the following configuration:

```python
{
  "mmc": "true",
  "regions": "de",
  "config": {
    "detection_mode": "vehicle"
  }
}
```

### Explanation

* `mmc=true` → enables make/model/color/year
* `detection_mode=vehicle` → works without visible plate
* `regions=de` → optimized for Germany

---

## 🧾 Data Extracted

For each vehicle:

```json
{
  "make": "Audi",
  "model": "e-tron",
  "year_start": 2017,
  "year_end": 2021,
  "color": "white",
  "orientation": "Front",
  "direction": 289,
  "confidence_score": 0.28
}
```

---

## 🧠 Multi-Candidate Handling

The system stores **all prediction candidates**, not just the best:

```json
"make_model_candidates": [
  {"make": "Audi", "model": "e-tron", "score": 0.278},
  {"make": "Audi", "model": "Q8", "score": 0.189}
]
```

This enables:

* better accuracy via aggregation
* future ML improvements

---

## ⏱️ Timestamp Tracking

Each record includes:

* `process_start_time` → when processing started
* `process_duration_sec` → total processing time
* `processed_at` → Firebase server timestamp

---

## 🔐 Privacy Considerations

* License plates are **never stored**
* All API responses are sanitized:

```python
r["plate"] = "REDACTED"
```

---

## 🗄️ Firestore Schema

Collection: `vehicles`

```json
{
  "make": "Audi",
  "model": "e-tron",
  "color": "white",
  "year_start": 2017,
  "year_end": 2021,
  "confidence_score": 0.28,

  "image_url": "...",

  "process_start_time": "...",
  "process_duration_sec": 1.2,
  "processed_at": "...",

  "drive_file_id": "...",

  "full_api_response": {...}
}
```

---

## 📂 Firebase Storage

Images are stored in:

```text
/cars/{filename}
```

---

## 🔒 Firestore Security Rules

Current setup:

```javascript
allow read, write: if false;
```

* Backend (Admin SDK) → ✅ allowed
* Frontend access → ❌ blocked

---

## 🚀 How It Works

1. System polls Google Drive for new images
2. Downloads image
3. Sends image to API
4. Finds best make/model prediction
5. Extracts metadata
6. Uploads image to Firebase
7. Saves data in Firestore

---

## ⚠️ Known Limitations

* API confidence is often low (~0.2–0.4)
* Results may vary across frames
* Blurred images reduce accuracy
* No deduplication yet

---

## 🔥 Next Steps

Planned improvements:

* 🔁 Deduplication system (avoid duplicate cars)
* 🎥 Video processing pipeline
* 📊 Multi-frame aggregation (voting system)
* 🧠 Replace API with custom classifier (YOLO + EfficientNet)
* 🌐 Web dashboard (React + Firebase)

---

## 🧪 Example Output

```text
✅ MMC SUCCESS: Audi e-tron (0.278) | ⏱ 1.23s
```

---

## 🛠️ Setup Instructions

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 2. Add config

```python
API_KEY = "your_api_key"
```

---

### 3. Add Firebase key

Place:

```text
firebase_key.json
```

---

### 4. Run system

```bash
python main.py
```

---

## 📌 Notes for Developers / LLMs

* API response must be parsed from:

  ```text
  vehicle → props
  ```
* Always preserve candidate lists
* Do not rely on plate data
* Firebase Admin SDK bypasses rules

---

# ✅ Final Conclusion

This system is a **scalable backend** for:

* real-time vehicle recognition
* data collection pipelines
* future AI model training
