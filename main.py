import os
import functions_framework
from google.cloud import storage
from src.emailer import send_chunk_email
from src.state_manager import update_state, get_last_chunk_id

@functions_framework.http
def daily_emailer(request):
    """
    HTTP Cloud Function to send the next book chunk.
    Required Env Vars:
      - GCS_BUCKET_NAME
      - GMAIL_USER
      - GMAIL_APP_PASSWORD
      - TARGET_EMAIL
    """
    # 1. Load Config
    bucket_name = os.environ.get('GCS_BUCKET_NAME')
    target_email = os.environ.get('TARGET_EMAIL')
    
    if not bucket_name or not target_email:
        return "Missing env vars: GCS_BUCKET_NAME or TARGET_EMAIL", 500

    book_title = "moby_dick" # Configurable?
    
    # 2. Determine Next Chunk
    last_id = get_last_chunk_id(book_title, bucket_name=bucket_name)
    next_id = last_id + 1
    
    chunk_filename = f"chunks/chunk_{next_id:03d}.html"
    
    # 3. Read Chunk from GCS
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(chunk_filename)
        
        if not blob.exists():
            msg = f"No more chunks found (checked {chunk_filename}). Book finished?"
            print(msg)
            return msg, 200
        
        content = blob.download_as_text()
        
    except Exception as e:
        return f"Error reading GCS: {e}", 500

    # 4. Send Email
    try:
        subject = f"Moby Dick - Part {next_id}"
        send_chunk_email(target_email, subject, content)
        
        # 5. Update State
        update_state(book_title, next_id, bucket_name=bucket_name)
        
        return f"Successfully sent chunk {next_id}", 200
        
    except Exception as e:
        print(f"Failed to send email: {e}")
        return f"Failed to send email: {e}", 500
