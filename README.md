# Call Me Ishmael

A project to parse EPUB books into daily email chunks.

## Setup

This project uses `uv` for dependency management.

1. Install `uv` if you haven't already.
2. Run `uv sync` to install dependencies.

## Usage

Currently, you can run the chunker script:

```bash
uv run src/html_chunker.py
```

This will parse `books/moby_dick.epub` and output HTML chunks into the `book_output/` directory.

## Project Structure

- `src/html_chunker.py`: Parses EPUB files and splits them into readable HTML chunks.
- `books/`: Place EPUB files here.
- `book_output/`: Generated HTML chunks are stored here.

## Future Plans

- Email service integration (once a day).
- Database/State management to track which chunk was last sent.
- Support for multiple books.
