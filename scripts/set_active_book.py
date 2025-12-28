import argparse
import sys
import os

# Add src to path so we can import state_manager
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from state_manager import set_book_active, load_state

def list_books(bucket_name):
    state = load_state(bucket_name)
    print(f"\n--- Books in State (Bucket: {bucket_name}) ---")
    for book, data in state.items():
        status = "✅ Active" if data.get("active") else "❌ Inactive"
        print(f"• {book}: {status} (Last Chunk: {data.get('last_chunk_id', 0)})")
    print("---------------------------------------------")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage active books in Call Me Ishmael state.")
    parser.add_argument("book_id", nargs="?", help="The book ID to activate (e.g. moby_dick)")
    parser.add_argument("--bucket", default="call-me-ishmael-graydon", help="GCS Bucket Name")
    parser.add_argument("--list", action="store_true", help="List all books and their status")
    parser.add_argument("--deactivate", action="store_true", help="Deactivate the specified book instead of activating it")

    args = parser.parse_args()
    
    if args.list:
        list_books(args.bucket)
        sys.exit(0)

    if not args.book_id:
        list_books(args.bucket)
        print("\nError: Please specify a book_id to activate/deactivate.")
        sys.exit(1)

    active_status = not args.deactivate
    print(f"Setting '{args.book_id}' active={active_status} in bucket '{args.bucket}'...")
    
    try:
        set_book_active(args.book_id, active_status, bucket_name=args.bucket)
        print("Success! State updated.")
        list_books(args.bucket)
    except Exception as e:
        print(f"Error updating state: {e}")
