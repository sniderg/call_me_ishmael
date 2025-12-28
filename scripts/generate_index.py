
import os
import glob

def generate_index(output_dir="book_output"):
    # 1. Find all book directories
    book_dirs = [d for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d))]
    
    book_links = ""
    
    for book_id in book_dirs:
        # Skip if it's not a book folder (e.g. random dir) - though we shouldn't have any
        book_path = os.path.join(output_dir, book_id)
        
        # 2. Generate Index for THIS Book
        html_files = sorted(glob.glob(os.path.join(book_path, "chunk_*.html")))
        if not html_files:
            continue
            
        list_items = ""
        for file_path in html_files:
            filename = os.path.basename(file_path)
            chunk_id = filename.replace("chunk_", "").replace(".html", "")
            list_items += f'<li><a href="{filename}">Part {chunk_id}</a></li>\n'
            
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
        </style>
    </head>
    <body>
        <h1>Call Me Ishmael: Library</h1>
        <p>Your collection of daily readings.</p>
        <ul>
            {book_links}
        </ul>
    </body>
    </html>
    """
    
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(root_index_html)
    print(f"Generated root library index")

if __name__ == "__main__":
    generate_index()
