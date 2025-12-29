import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

import json

def create_html_chunk(content_blocks, chunk_id, total_chunks, book_title, book_id, chapter_list=None, next_chunk_id=None):
    """Wraps the raw paragraphs in a nice HTML email template."""
    
    # GCS Authenticated URL (requires Google login)
    epub_url = f"https://storage.cloud.google.com/call-me-ishmael-graydon/books/{book_id}/ebook.epub"
    
    # Firebase Hosting URLs
    index_url = f"https://gen-lang-client-0138429727.web.app/{book_id}/"
    hosting_url = f"https://gen-lang-client-0138429727.web.app/{book_id}/chunk_{chunk_id:03d}.html"
    
    if next_chunk_id:
        next_url = f"https://gen-lang-client-0138429727.web.app/{book_id}/chunk_{next_chunk_id:03d}.html"
        footer_link = f'<a href="{next_url}">Jump to tomorrow\'s part</a>'
    else:
        footer_link = "<span>End of Book</span>"

    # Format chapter info
    chapter_info = ""
    if chapter_list:
        joined_chapters = ", ".join(chapter_list)
        chapter_info = f", covering: {joined_chapters}"

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                margin: 0;
                padding: 0;
                background-color: #fdf6e3; 
                font-family: Georgia, serif; 
            }}
            .container {{
                max-width: 550px; 
                margin: 0 auto; 
                padding: 40px 20px;
                background-color: #ffffff;
                color: #333; 
                line-height: 1.6; 
                font-size: 18px;
                border-radius: 8px; /* Optional: adds a slight card effect */
                box-shadow: 0 2px 5px rgba(0,0,0,0.05); /* Optional: subtle shadow */
            }}
            /* Specific for dark mode readers if needed, but keeping it simple for now */
            h1, h2, h3 {{ color: #2c3e50; margin-top: 0; }}
            .footer {{ 
                margin-top: 40px; 
                font-size: 0.8em; 
                color: #888; 
                border-top: 1px solid #eee; 
                padding-top: 20px; 
                text-align: center;
            }}
            .footer p {{ margin: 5px 0; }}
            .footer a {{
                color: #888;
                text-decoration: underline;
            }}
            .book-title a {{
                color: #2c3e50;
                text-decoration: none;
            }}
            .book-title a:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="container">
             <h2 class="book-title"><a href="{index_url}">{book_title}</a> <span style="font-size:0.6em; color:#777; font-weight: normal;">(Part {chunk_id} of {total_chunks}{chapter_info})</span></h2>
            
            {"".join(content_blocks)}
            
            <div class="footer">
                <p>End of Part {chunk_id}. Next part arrives tomorrow.</p>
                <p><a href="{hosting_url}">Read this part online</a> | {footer_link}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    output_dir = f"book_output/{book_id}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filename = f"{output_dir}/chunk_{chunk_id:03d}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_template)
    return filename

def process_epub(epub_path, book_id, target_words=2500):
    book = epub.read_epub(epub_path)
    # Try to get title, fall back to book_id if missing
    try:
        title = book.get_metadata('DC', 'title')[0][0]
    except:
        title = book_id.replace("_", " ").title()
    
    current_blocks = []
    current_word_count = 0
    all_chunks_data = [] # Store chunks temporarily
    
    # Track chapters found in the current buffer
    current_chapters = []
    
    # 1. Iterate over every document in the book (Chapters, Intro, etc.)
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_body_content(), 'html.parser')
        
        # Get all top-level tags to iterate
        tags = soup.body.find_all(recursive=False)
        if not tags:
            continue
            
        # Efficiently calculate remaining words for this chapter
        chapter_word_counts = [len(tag.get_text().split()) for tag in tags]
        total_chapter_words = sum(chapter_word_counts)
        words_processed_in_chapter = 0
        
        for i, tag in enumerate(tags):
            tag_html = str(tag)
            text_len = chapter_word_counts[i]
            
            # --- EXTRACT CHAPTER TITLES ---
            # If tag is H1 or H2, treat as chapter title
            if tag.name in ['h1', 'h2']:
                header_text = tag.get_text().strip()
                if header_text and len(header_text) < 100: # Sanity check length
                    if header_text not in current_chapters:
                        current_chapters.append(header_text)

            # Check remaining words in this chapter (including current tag)
            remaining_in_chapter = total_chapter_words - words_processed_in_chapter
            
            # Check if adding this would exceed limit
            if current_word_count + text_len > target_words and current_word_count > 500:
                
                # RULE 1: Relax limit if we can finish the chapter soon
                if remaining_in_chapter < 750:
                    pass # Don't split
                else:
                    # RULE 2: Avoid ending on a header
                    last_block_is_header = False
                    if current_blocks:
                        last_html = current_blocks[-1].strip()
                        if any(last_html.startswith(f"<{h}") for h in ['h1','h2','h3','h4','h5','h6']):
                            last_block_is_header = True
                    
                    if last_block_is_header:
                        header_to_move = current_blocks.pop()
                        # If we move a header, we must also move it from 'current_chapters' 
                        # to the next chunk if it was just added. 
                        # (Simplification: just add it to next chunk's chapters, it's okay if it appears in both manifests slightly)
                        
                        all_chunks_data.append({
                            'blocks': current_blocks,
                            'chapters': list(current_chapters) # Snapshot
                        })
                        
                        current_blocks = [header_to_move]
                        header_soup = BeautifulSoup(header_to_move, 'html.parser')
                        current_word_count = len(header_soup.get_text().split())
                        
                        # Reset chapters for next chunk, but re-add the moved header
                        header_text = header_soup.get_text().strip()
                        current_chapters = [header_text] if header_text else []
                    else:
                        all_chunks_data.append({
                            'blocks': current_blocks,
                            'chapters': list(current_chapters)
                        })
                        current_blocks = []
                        current_word_count = 0
                        current_chapters = []
            
            current_blocks.append(tag_html)
            current_word_count += text_len
            words_processed_in_chapter += text_len

    # 3. Capture final chunk
    if current_blocks:
        all_chunks_data.append({
            'blocks': current_blocks,
            'chapters': list(current_chapters)
        })
        
    # 4. Generate Files & Manifest
    total_chunks = len(all_chunks_data)
    manifest = []
    
    for i, data in enumerate(all_chunks_data):
        chunk_num = i + 1
        blocks = data['blocks']
        chapters = data['chapters']
        
        # Determine next chunk ID for link
        next_chunk_id = (chunk_num + 1) if chunk_num < total_chunks else None
        
        create_html_chunk(blocks, chunk_num, total_chunks, title, book_id, 
                          chapter_list=chapters, next_chunk_id=next_chunk_id)
        
        manifest.append({
            "chunk_id": chunk_num,
            "chapters": chapters
        })

    # Save Manifest
    manifest_path = f"book_output/{book_id}/manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Created {total_chunks} chunks & manifest for '{title}'")

# --- USAGE ---
if __name__ == "__main__":
    # Ensure output directory exists
    if not os.path.exists('book_output'):
        os.makedirs('book_output')

    # Process all EPUBs in books/ directory
    books_dir = "books"
    if os.path.exists(books_dir):
        epub_files = [f for f in os.listdir(books_dir) if f.endswith(".epub")]
        
        if not epub_files:
            print(f"No .epub files found in {books_dir}/")
        
        for epub_file in epub_files:
            # Create a book_id from filename (e.g., "moby_dick.epub" -> "moby_dick")
            book_id = os.path.splitext(epub_file)[0]
            epub_path = os.path.join(books_dir, epub_file)
            
            print(f"--- Processing {book_id} ---")
            process_epub(epub_path, book_id)
    else:
        print(f"Directory {books_dir} not found.")
