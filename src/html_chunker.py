import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

def create_html_chunk(content_blocks, chunk_id, total_chunks, book_title, book_id):
    """Wraps the raw paragraphs in a nice HTML email template."""
    
    # GCS Authenticated URL (requires Google login)
    epub_url = f"https://storage.cloud.google.com/call-me-ishmael-graydon/books/{book_id}/ebook.epub"
    
    # Firebase Hosting URL
    hosting_url = f"https://gen-lang-client-0138429727.web.app/{book_id}/chunk_{chunk_id:03d}.html"

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
        </style>
    </head>
    <body>
        <div class="container">
            <h2>{book_title} <span style="font-size:0.6em; color:#777; font-weight: normal;">(Part {chunk_id} of {total_chunks})</span></h2>
            
            {"".join(content_blocks)}
            
            <div class="footer">
                <p>End of Part {chunk_id}. Next part arrives tomorrow.</p>
                <p><a href="{hosting_url}">Read this part online</a> | <a href="{epub_url}">Download full eBook</a></p>
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
    
    # 1. Iterate over every document in the book (Chapters, Intro, etc.)
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_body_content(), 'html.parser')
        
        # 2. Iterate over top-level elements (p, h1, div, etc.)
        for tag in soup.body.find_all(recursive=False):
            tag_html = str(tag)
            text_len = len(tag.get_text().split())
            
            if current_word_count + text_len > target_words and current_word_count > 500:
                all_chunks_data.append(current_blocks)
                
                # Reset
                current_blocks = []
                current_word_count = 0
            
            current_blocks.append(tag_html)
            current_word_count += text_len

    # 3. Capture final chunk
    if current_blocks:
        all_chunks_data.append(current_blocks)
        
    # 4. Generate Files with Total Count
    total_chunks = len(all_chunks_data)
    for i, blocks in enumerate(all_chunks_data):
        chunk_num = i + 1
        create_html_chunk(blocks, chunk_num, total_chunks, title, book_id)
        
    print(f"Created {total_chunks} chunks for '{title}'")

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
