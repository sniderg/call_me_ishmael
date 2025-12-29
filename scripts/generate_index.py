
import os
import glob

def generate_index(output_dir="book_output"):
    # 1. Find all book directories
    book_dirs = [d for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d))]
    
    book_links = ""
    
    for book_id in book_dirs:
        # Skip if it's not a book folder
        book_path = os.path.join(output_dir, book_id)
        
        # Load Manifest if available
        import json
        manifest = {}
        manifest_path = os.path.join(book_path, "manifest.json")
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest_list = json.load(f)
                    # Convert list to dict for lookup: {1: ["Ch1"], 2: ...}
                    manifest = {item["chunk_id"]: item["chapters"] for item in manifest_list}
            except Exception as e:
                print(f"Warning: Failed to load manifest for {book_id}: {e}")
        
        # 2. Generate Index for THIS Book
        html_files = sorted(glob.glob(os.path.join(book_path, "chunk_*.html")))
        if not html_files:
            continue
            
        list_items = ""
        for file_path in html_files:
            filename = os.path.basename(file_path)
            chunk_id_str = filename.replace("chunk_", "").replace(".html", "")
            chunk_id = int(chunk_id_str)
            
            # Get chapter info
            chapters = manifest.get(chunk_id, [])
            chapter_text = ""
            if chapters:
                chapter_text = f' <span class="chapters">({", ".join(chapters)})</span>'
            
            list_items += f'<li><a href="{filename}">Part {chunk_id_str}</a>{chapter_text}</li>\n'
            
        book_title = book_id.replace("_", " ").title()
        
        book_index_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{book_title} - Daily Chunks</title>
            <style>
                body {{ font-family: Georgia, serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; background: #fdf6e3; color: #333; }}
                h1 {{ border-bottom: 2px solid #ddd; padding-bottom: 10px; }}
                ul {{ list-style-type: none; padding: 0; }}
                li {{ margin: 10px 0; }}
                a {{ text-decoration: none; color: #d35400; font-weight: bold; font-size: 1.1em; }}
                a:hover {{ text-decoration: underline; }}
                .chapters {{ font-size: 0.9em; color: #777; margin-left: 10px; }}
                .back {{ margin-top: 20px; display: block; font-size: 0.9em; color: #777; }}
            </style>
        </head>
        <body>
            <h1>{book_title}</h1>
            <p>Table of Contents</p>
            <ul>
                {list_items}
            </ul>
            <a href="../index.html" class="back">← Back to Library</a>
        </body>
        </html>
        """
        
        with open(os.path.join(book_path, "index.html"), "w", encoding="utf-8") as f:
            f.write(book_index_html)
        print(f"Generated index for {book_id}")
        
        # Add to main library list
        # Optionally show book author or chunk count here if we wanted
        book_links += f'<li><a href="{book_id}/index.html">{book_title}</a></li>\n'

    # 3. Generate Root Library Index
    root_index_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Call Me Ishmael - Library</title>
        <style>
            body {{ font-family: Georgia, serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; background: #fdf6e3; color: #333; }}
            h1 {{ border-bottom: 2px solid #ddd; padding-bottom: 10px; }}
            ul {{ list-style-type: none; padding: 0; }}
            li {{ margin: 15px 0; font-size: 1.2em; }}
            a {{ text-decoration: none; color: #2c3e50; font-weight: bold; }}
            a:hover {{ text-decoration: underline; color: #d35400; }}
            .footer {{ margin-top: 50px; border-top: 1px solid #ddd; padding-top: 20px; font-size: 0.9em; color: #666; }}
            .footer a {{ color: #666; font-weight: normal; }}
        </style>
    </head>
    <body>
        <h1>Call Me Ishmael: Library</h1>
        <p>Your collection of daily readings.</p>
        <ul>
            {book_links}
        </ul>
        <div class="footer">
            <p>Project by Graydon Snider. <a href="https://github.com/sniderg/call_me_ishmael">View Source on GitHub</a></p>
        </div>
    </body>
    </html>
    """
    
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(root_index_html)
    print(f"Generated root library index")

if __name__ == "__main__":
    generate_index()
