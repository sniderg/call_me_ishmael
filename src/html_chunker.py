import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

def create_html_chunk(content_blocks, chunk_id, book_title):
    """Wraps the raw paragraphs in a nice HTML email template."""
    
    # GCS Authenticated URL (requires Google login)
    epub_url = f"https://storage.cloud.google.com/call-me-ishmael-graydon/moby_dick.epub"
    
    # Firebase Hosting URL
    hosting_url = f"https://gen-lang-client-0138429727.web.app/chunk_{chunk_id:03d}.html"

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
            <h2>{book_title} <span style="font-size:0.6em; color:#777; font-weight: normal;">(Part {chunk_id})</span></h2>
            
            {"".join(content_blocks)}
            
            <div class="footer">
                <p>End of Part {chunk_id}. Next part arrives tomorrow.</p>
                <p><a href="{hosting_url}">Read this part online</a> | <a href="{epub_url}">Download full eBook</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    filename = f"book_output/chunk_{chunk_id:03d}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_template)
    return filename

def process_epub(epub_path, target_words=2500):
    book = epub.read_epub(epub_path)
    title = book.get_metadata('DC', 'title')[0][0]
    
    current_blocks = []
    current_word_count = 0
    chunk_counter = 1
    
    # 1. Iterate over every document in the book (Chapters, Intro, etc.)
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_body_content(), 'html.parser')
        
        # 2. Iterate over top-level elements (p, h1, div, etc.)
        # We process element-by-element to avoid splitting mid-paragraph
        for tag in soup.body.find_all(recursive=False):
            tag_html = str(tag)
            text_len = len(tag.get_text().split())
            
            # If adding this paragraph pushes us way over the limit, dump the current chunk first
            if current_word_count + text_len > target_words and current_word_count > 500:
                create_html_chunk(current_blocks, chunk_counter, title)
                print(f"Created chunk {chunk_counter:03d} ({current_word_count} words)")
                
                # Reset
                chunk_counter += 1
                current_blocks = []
                current_word_count = 0
            
            current_blocks.append(tag_html)
            current_word_count += text_len

    # 3. Save any leftovers as the final chunk
    if current_blocks:
        create_html_chunk(current_blocks, chunk_counter, title)
        print(f"Created chunk {chunk_counter:03d} (Final Part)")

# --- USAGE ---
# Make sure you have a folder called 'book_output'
if not os.path.exists('book_output'):
    os.makedirs('book_output')

process_epub("books/moby_dick.epub")
