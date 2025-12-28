import os
import argparse
from dotenv import load_dotenv
from emailer import send_chunk_email
from state_manager import update_state, get_last_chunk_id

# Load environment variables
load_dotenv()

def test_email(chunk_id, force=False):
    # Check if target email is set
    target_email = os.getenv('TARGET_EMAIL')
    if not target_email:
        print("Error: TARGET_EMAIL not set in .env")
        return

    # Construct the path to the chunk
    chunk_path = f"book_output/chunk_{chunk_id:03d}.html"
    
    if not os.path.exists(chunk_path):
        print(f"Error: Chunk file {chunk_path} does not exist.")
        return

    # Check state management
    book_title = "moby_dick" # Hardcoded for now per current structure
    last_id = get_last_chunk_id(book_title)
    
    if chunk_id <= last_id and not force:
        print(f"Skipping chunk {chunk_id}: Already sent (last sent: {last_id}). Use --force to override.")
        return

    # Read the content
    with open(chunk_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"Sending chunk {chunk_id} to {target_email}...")
    
    try:
        subject = f"Moby Dick - Part {chunk_id}"
        send_chunk_email(target_email, subject, content)
        
        # Update state
        update_state(book_title, chunk_id)
        print(f"Success! State updated. Last chunk is now {chunk_id}.")
        
    except Exception as e:
        print(f"Failed to send: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test sending a specific book chunk via email.")
    parser.add_argument("--chunk", type=int, required=True, help="The chunk ID to send (e.g., 1)")
    parser.add_argument("--force", action="store_true", help="Send even if already marked as sent")
    
    args = parser.parse_args()
    test_email(args.chunk, args.force)
