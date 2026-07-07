"""Reusable test data factories."""

SAMPLE_USER = {
    "phone": "9000000001",
    "password": "testpass123",
    "full_name": "Sample Farmer",
    "role": "farmer",
}

SAMPLE_PROFILE = {
    "full_name": "Sample Farmer",
    "preferred_lang": "en",
    "location": {
        "state": "Punjab",
        "district": "Ludhiana",
        "village": "Test Village",
        "coordinates": {"lat": 30.9, "lng": 75.8},
    },
    "farm_size_acres": 3.5,
    "soil_type": "loamy",
    "irrigation_type": "drip",
    "primary_crops": ["wheat", "rice"],
}

SAMPLE_DISEASE_QUERY = {
    "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    "crop_name": "wheat",
}

SAMPLE_CHAT_QUERY = {
    "query": "What is the best fertilizer for wheat in Punjab?",
    "language": "en",
}

SAMPLE_MARKET_QUERY = {
    "commodity": "wheat",
    "district": "Ludhiana",
    "state": "Punjab",
}
