import json
import os
from datetime import datetime
from google.cloud import storage

STATE_FILE = "sending_state.json"

def load_state(bucket_name=None):
    if bucket_name:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(STATE_FILE)
        if blob.exists():
            return json.loads(blob.download_as_string())
        return {}
    
    # Fallback to local file
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_state(state, bucket_name=None):
    if bucket_name:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(STATE_FILE)
        blob.upload_from_string(json.dumps(state, indent=4))
        return

    # Fallback to local file
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

def get_last_chunk_id(book_title, bucket_name=None):
    state = load_state(bucket_name)
    return state.get(book_title, {}).get("last_chunk_id", 0)

def update_state(book_title, chunk_id, bucket_name=None):
    state = load_state(bucket_name)
    
    # Get existing book state or initialize
    book_state = state.get(book_title, {})
    
    # Update fields (preserving others like 'active')
    book_state["last_chunk_id"] = chunk_id
    book_state["last_sent_at"] = datetime.now().isoformat()
    
    state[book_title] = book_state
    save_state(state, bucket_name)

def set_book_active(book_title, active: bool, bucket_name=None):
    state = load_state(bucket_name)
    
    # Get existing book state or initialize
    book_state = state.get(book_title, {})
    book_state["active"] = active
    
    state[book_title] = book_state
    save_state(state, bucket_name)
