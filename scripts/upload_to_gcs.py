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

    # 1. Upload Chunks
    files = [f for f in os.listdir(source_dir) if f.endswith(".html")]
    if not files:
        print(f"No HTML files found in {source_dir}. Run chunker first.")
        # If no chunks, we still might want to upload the EPUB, so don't return here.
    else:
        print(f"Found {len(files)} chunks to upload...")
        for filename in files:
            local_path = os.path.join(source_dir, filename)
            blob_name = f"chunks/{filename}"
            
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(local_path)
            print(f"Uploading {filename} -> gs://{bucket_name}/{blob_name}")
        
    # 2. Upload Original EPUB
    epub_local = "books/moby_dick.epub"
    if os.path.exists(epub_local):
        blob_epub = bucket.blob("moby_dick.epub") # Upload to root of bucket
        blob_epub.upload_from_filename(epub_local)
        print(f"Uploading {epub_local} -> gs://{bucket_name}/moby_dick.epub")
    else:
        print(f"Warning: {epub_local} not found, skipping EPUB upload.")

    print("Upload complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload chunks to GCS")
    parser.add_argument("--bucket", required=True, help="Target GCS bucket name")
    args = parser.parse_args()
    
    upload_chunks(args.bucket)
