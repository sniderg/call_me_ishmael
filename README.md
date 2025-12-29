# Call Me Ishmael

A serverless EPUB-to-Email automation system that delivers your favorite books in bite-sized daily chunks.

## Features

- **Multi-Book Support**: Manage multiple libraries at once. Each book maintains its own independent state and styling.
- **Intelligent Chunking**: Extracts and labels chunks by chapter (e.g., "Part 5 of 89, covering: Chapter 10, Chapter 11"). 
- **Active State Control**: Explicitly control which books are current being emailed using an `active` flag. Books automatically deactivate and notify you upon completion.
- **GCP Serverless Architecture**:
  - **Cloud Functions**: Handles daily email dispatch.
  - **Cloud Storage (GCS)**: Stores HTML chunks and book state.
  - **Cloud Scheduler**: Triggers daily delivery at your preferred time (default 7:00 AM).
  - **Firebase Hosting**: Serves a web-based "Library" and Table of Contents for easy reading.
- **Enhanced Navigation**: Emails include links back to the book's index and "Jump to tomorrow's part" for continued reading.

## Setup

This project uses `uv` for dependency management.

1.  **Install dependencies**: `uv sync`
2.  **Environment**: Create a `.env` file with Gmail SMTP credentials and GCS bucket info.
3.  **Authentication**: Run `gcloud auth application-default login` for local script access to GCP.

## Core Scripts

- `uv run src/html_chunker.py`: Parses EPUBs in `books/`, generates HTML chunks with chapter metadata, and creates a `manifest.json` per book.
- `uv run scripts/generate_index.py`: Creates a root library index and per-book Table of Contents.
- `uv run scripts/upload_to_gcs.py`: Syncs generated chunks and metadata to Google Cloud Storage.
- `uv run scripts/set_active_book.py`: Easily list books and toggle which ones are emailed via CLI.
- `./deploy_gcp.sh`: Deploys the delivery Cloud Function and Scheduler job.

## Adding a New Book

1.  Place the `.epub` in the `books/` directory.
2.  Run `uv run src/html_chunker.py` to generate the chunks.
3.  Run `uv run scripts/generate_index.py` to update the library indices.
4.  Run `uv run scripts/upload_to_gcs.py` to sync to the cloud.
5.  Run `firebase deploy` to update the web library.
6.  Activate the book for mailing: `uv run scripts/set_active_book.py <book_id>`

## Project Structure

- `src/`: Core application logic (chunking, emailer, state management).
- `scripts/`: Maintenance scripts for indexing, uploading, and state control.
- `books/`: Source EPUB files.
- `book_output/`: Locally generated HTML chunks and indices.
- `main.py`: Entry point for the Google Cloud Function.
- `sending_state.json`: (In GCS) Tracks reading progress and active status for all books.
