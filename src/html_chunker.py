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
    index_url = f"https://call-me-ishmael.web.app/{book_id}/"
    hosting_url = f"https://call-me-ishmael.web.app/{book_id}/chunk_{chunk_id:03d}"
    
    if next_chunk_id:
        next_url = f"https://call-me-ishmael.web.app/{book_id}/chunk_{next_chunk_id:03d}"
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

import re

def clean_title(text):
    """Normalize chapter titles."""
    if not text:
        return ""
    
    # Handle all uppercase (e.g. "CHAPTER 1. THE WHALE")
    if text.isupper():
        text = text.title()
    
    # Handle specific "CHAPTER" casing if mixed (e.g. "CHAPTER 1. The Whale")
    if text.upper().startswith("CHAPTER"):
        text = "Chapter" + text[7:]

    # Fix Roman Numerals (e.g., "Iii" -> "III", "Iv" -> "IV")
    # This looks for words that consist entirely of Roman numeral characters
    def roman_upscale(match):
        word = match.group(0)
        # Check if it's purely Roman characters (I, V, X, L, C, D, M)
        if all(c.upper() in "IVXLCDM" for c in word) and len(word) > 0:
            return word.upper()
        return word

    text = re.sub(r'\b[a-zA-Z]+\b', roman_upscale, text)
    
    # If the title is JUST a Roman numeral (e.g. "I", "IV", "X."), prepend "Chapter"
    # This helps with books like "Through the Looking Glass" that use bare numerals
    if re.match(r'^[IVXLCDM]+\.?$', text):
        text = "Chapter " + text.replace(".", "")
        
    return text.strip()

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
    last_chapter_title = "Start" # Default for beginning
    
    # 1. Extract Cover Image
    cover_item = None
    
    # Try getting cover by ID from metadata
    try:
        cover_id = book.get_metadata('OPF', 'cover')[0][0]
        cover_item = book.get_item_with_id(cover_id)
    except:
        pass
        
    # If not found, look for items marked as cover
    if not cover_item:
        covers = list(book.get_items_of_type(ebooklib.ITEM_COVER))
        if covers:
            cover_item = covers[0]
            
    # If still not found, search images for "cover" in name
    if not cover_item:
        for img in book.get_items_of_type(ebooklib.ITEM_IMAGE):
            if 'cover' in img.get_name().lower() or 'cover' in img.get_id().lower():
                cover_item = img
                break
    
    # Save the cover if found
    if cover_item:
        file_name = cover_item.get_name()
        ext = os.path.splitext(file_name)[1]
        
        # If extraction failed or weird name, default to .jpg
        if not ext or len(ext) > 5:
            ext = ".jpg"
            
        cover_path = f"book_output/{book_id}/cover{ext}"
        output_dir = f"book_output/{book_id}"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        with open(cover_path, "wb") as f:
            f.write(cover_item.get_content())
        print(f"Saved cover image to {cover_path}")
    else:
        print("No cover image found.")

    # Create images directory
    images_output_dir = f"book_output/{book_id}/images"
    if not os.path.exists(images_output_dir):
        os.makedirs(images_output_dir)

    # 2. Iterate over every document in the book (Chapters, Intro, etc.)
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_body_content(), 'html.parser')
        
        # --- HANDLE IMAGES ---
        # Find all images in this document and process them
        for img_tag in soup.find_all('img'):
            src = img_tag.get('src')
            if not src:
                continue
                
            # Resolve absolute path within EPUB based on current document path
            # EPUB paths are always forward slashes
            doc_dir = os.path.dirname(item.get_name())
            
            # Simple manual path resolution to avoid OS separator issues
            if doc_dir:
                absolute_href = f"{doc_dir}/{src}"
            else:
                absolute_href = src
                
            # Handle ".." in path
            parts = absolute_href.split('/')
            resolved_parts = []
            for part in parts:
                if part == '..':
                    if resolved_parts:
                        resolved_parts.pop()
                elif part != '.':
                    resolved_parts.append(part)
            resolved_href = "/".join(resolved_parts)

            # Find the image item in the book
            img_item = book.get_item_with_href(resolved_href)
            
            if img_item:
                # Use the basename for the saved file
                img_filename = os.path.basename(resolved_href)
                save_path = f"{images_output_dir}/{img_filename}"
                
                # Save image if not already saved
                if not os.path.exists(save_path):
                    with open(save_path, "wb") as f:
                        f.write(img_item.get_content())
                
                # Update the source to point to our hosted images folder
                # We use absolute URL so it works in Emails AND on the website (regardless of current path/route)
                img_tag['src'] = f"https://call-me-ishmael.web.app/{book_id}/images/{img_filename}"
                img_tag['style'] = "max-width: 100%; height: auto; display: block; margin: 20px auto;"
            else:
                 print(f"Warning: Could not find image {resolved_href}")

        # Get all top-level tags to iterate from the modified soup
        tags = soup.body.find_all(recursive=False)
        
        # Flatten wrapper tags (section, div, article) to expose content
        # accurately, allowing us to split large chapters and find headers nested in sections
        while len(tags) == 1 and tags[0].name in ['div', 'section', 'article', 'main']:
            tags = tags[0].find_all(recursive=False)
            
        if not tags:
            continue
            
        # Efficiently calculate remaining words for this chapter
        # Note: Images now have text length 0, so we might want to add phantom words
        chapter_word_counts = [] 
        for tag in tags:
             text_count = len(tag.get_text().split())
             # Add weight for images to avoid huge emails with many images
             img_count = len(tag.find_all('img'))
             text_count += (img_count * 200) # 200 words equivalent per image
             chapter_word_counts.append(text_count)
             
        total_chapter_words = sum(chapter_word_counts)
        words_processed_in_chapter = 0
        
        for i, tag in enumerate(tags):
            tag_html = str(tag)
            text_len = chapter_word_counts[i]
            
            # --- EXTRACT CHAPTER TITLES ---
            # If tag is H1 or H2, treat as chapter title
            # Also handle hgroup (common in standardebooks)
            
            title_text = None
            if tag.name in ['h1', 'h2']:
                title_text = tag.get_text().strip()
            elif tag.name == 'hgroup':
                 # Find first h1/h2 in group
                 header = tag.find(['h1', 'h2'])
                 if header:
                     title_text = header.get_text().strip()

            if title_text:
                if len(title_text) < 100: # Sanity check length
                    cleaned_text = clean_title(title_text)
                    last_chapter_title = cleaned_text
                    if cleaned_text not in current_chapters:
                        current_chapters.append(cleaned_text)

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
 
                        # Save current chunk
                        # Determine label: if no new chapters, use continued
                        chunk_labels = list(current_chapters)
                        if not chunk_labels:
                            chunk_labels = [f"{last_chapter_title} (cont.)"]

                        all_chunks_data.append({
                            'blocks': current_blocks,
                            'chapters': chunk_labels
                        })
                        
                        current_blocks = [header_to_move]
                        header_soup = BeautifulSoup(header_to_move, 'html.parser')
                        current_word_count = len(header_soup.get_text().split())
                        
                        # Reset: The moved header is now the "current" chapter for the next chunk
                        header_text = clean_title(header_soup.get_text().strip())
                        current_chapters = [header_text] if header_text else []
                        if header_text:
                            last_chapter_title = header_text
                    else:
                        # Determine label
                        chunk_labels = list(current_chapters)
                        if not chunk_labels:
                            chunk_labels = [f"{last_chapter_title} (cont.)"]

                        all_chunks_data.append({
                            'blocks': current_blocks,
                            'chapters': chunk_labels
                        })
                        current_blocks = []
                        current_word_count = 0
                        current_chapters = []
            
            current_blocks.append(tag_html)
            current_word_count += text_len
            words_processed_in_chapter += text_len

    # 3. Capture final chunk
    if current_blocks:
        chunk_labels = list(current_chapters)
        if not chunk_labels:
             chunk_labels = [f"{last_chapter_title} (cont.)"]
             
        all_chunks_data.append({
            'blocks': current_blocks,
            'chapters': chunk_labels
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
