# storage/models.py
from dataclasses import dataclass, asdict
from typing import Any, Dict

@dataclass
class VehicleDetection:
    """
    Blueprint for a single vehicle detection document in Firestore.
    Ensures consistent data types for querying and analytics.
    """
    # Searchable Strings
    make: str
    model: str
    color: str
    orientation: str
    
    # Numeric values for range queries (>, <, ==)
    year_start: int
    year_end: int
    confidence_score: float
    
    # Metadata & Links
    image_url: str
    drive_file_id: str
    
    # Firestore Server Timestamp
    processed_at: Any  
    
    # Complete API response for future-proofing
    full_api_response: Dict[str, Any]

    def to_dict(self):
        """Converts the dataclass instance to a dictionary for Firestore .set()"""
        return asdict(self)