import os
import functions_framework
from google.cloud import storage
from src.emailer import send_chunk_email
from src.state_manager import update_state, get_last_chunk_id

@functions_framework.http
def daily_emailer(request):
    """
    HTTP Cloud Function to send the next book chunk for ALL active books.
    """
    # 1. Load Config
    bucket_name = os.environ.get('GCS_BUCKET_NAME')
    target_email = os.environ.get('TARGET_EMAIL')
    
    if not bucket_name or not target_email:
        return "Missing env vars: GCS_BUCKET_NAME or TARGET_EMAIL", 500

    # 2. Load State to find active books
    from src.state_manager import load_state, update_state, set_book_active
    
    state = load_state(bucket_name)
    if not state:
        return "No books found in sending_state.json", 200
        
    results = []
    
    # 3. Process Each Active Book
    for book_id, book_data in state.items():
        # Skip inactive books
        if not book_data.get("active", False):
            continue

        try:
            # Determine Next Chunk
            last_id = book_data.get("last_chunk_id", 0)
            next_id = last_id + 1
            
            # New Path: books/<book_id>/chunks/chunk_XXX.html
            chunk_filename = f"books/{book_id}/chunks/chunk_{next_id:03d}.html"
            
            # Read Chunk from GCS
            storage_client = storage.Client()
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(chunk_filename)
            
            book_title = book_id.replace("_", " ").title()

            if not blob.exists():
                # --- BOOK FINISHED LOGIC ---
                msg = f"[{book_id}] Book completed! No chunk {next_id} found."
                print(msg)
                
                # 1. Send Completion Email
                completion_subject = f"{book_title} - Completed"
                completion_body = f"""
                <html>
                <body>
                    <h2>Congratulations!</h2>
                    <p>You have finished reading <strong>{book_title}</strong>.</p>
                    <p>This book has now been pushed to the archives.</p>
                    <p>Reply to this email if you'd like to start a new one!</p>
                </body>
                </html>
                """
                send_chunk_email(target_email, completion_subject, completion_body)
                
                # 2. Mark as Inactive
                set_book_active(book_id, False, bucket_name=bucket_name)
                
                results.append(f"[{book_id}] Finished & Deactivated.")
                continue
            
            content = blob.download_as_text()
            
            # Send Email
            subject = f"{book_title} - Part {next_id}"
            send_chunk_email(target_email, subject, content)
            
            # Update State
            update_state(book_id, next_id, bucket_name=bucket_name)
            
            results.append(f"[{book_id}] Sent chunk {next_id}")
            
        except Exception as e:
            err_msg = f"[{book_id}] Error: {str(e)}"
            print(err_msg)
            results.append(err_msg)

    return "\n".join(results), 200
