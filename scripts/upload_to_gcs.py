import os
import argparse
import glob
from google.cloud import storage

def upload_chunks(bucket_name, source_dir="book_output"):
    """
    Uploads all HTML chunks from source_dir to gs://bucket_name/chunks/
    """
    client = storage.Client()
    try:
        bucket = client.get_bucket(bucket_name)
    except Exception:
        print(f"Bucket {bucket_name} not found. Please create it first.")
        return

    print(f"Uploading to gs://{bucket_name}/...")
    
    # 1. Identify Books from book_output directory
    if not os.path.exists(source_dir):
        print(f"Directory {source_dir} not found.")
        return

    book_ids = [d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))]
    
    if not book_ids:
        print("No book directories found in book_output/")
        return

    for book_id in book_ids:
        print(f"--- Processing {book_id} ---")
        book_dir = os.path.join(source_dir, book_id)
        
        # A. Upload Chunks
        files = [f for f in os.listdir(book_dir) if f.endswith(".html")]
        for filename in files:
            local_path = os.path.join(book_dir, filename)
            # GCS Path: books/<book_id>/chunks/<filename>
            blob_name = f"books/{book_id}/chunks/{filename}"
            
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(local_path)
            print(f"Uploading {filename} -> gs://{bucket_name}/{blob_name}")
            
        # B. Upload EPUB
        # Assuming local epub is at books/<book_id>.epub
        epub_local = f"books/{book_id}.epub"
        if os.path.exists(epub_local):
            blob_name = f"books/{book_id}/ebook.epub"
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(epub_local)
            print(f"Uploading {epub_local} -> gs://{bucket_name}/{blob_name}")
        else:
            print(f"Warning: {epub_local} not found, skipping EPUB upload.")

    print("Upload complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload chunks to GCS")
    parser.add_argument("--bucket", required=True, help="Target GCS bucket name")
    args = parser.parse_args()
    
    upload_chunks(args.bucket)
